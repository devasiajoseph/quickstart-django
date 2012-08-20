from django import forms
from django.conf import settings
from app.utilities import reply_object
from django.contrib.auth.models import User, check_password
from django.contrib.auth import authenticate, login
import requests
import re
from facebooksdk import Facebook
from django.db.models import Q
from app.models import UserProfile
from app.utilities import create_key, send_password_reset_email

attrs_dict = {'class': 'input-xlarge'}


class LoginForm(forms.Form):

    """
    Form for login
    """
    username = forms.RegexField(regex=r'^\w+$',
        max_length=30,
        widget=forms.TextInput(attrs=attrs_dict),
        label=("Username"),
        error_messages={'invalid':
            ("Username must contain only letters, numbers and underscores.")})
    password = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
        render_value=True),
        label=("Password"))

    remember_me = forms.BooleanField(widget=forms.CheckboxInput(),
                                     required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        The login functionality happens while cleaning
        """
        if 'username' in self.cleaned_data and 'password' in self.cleaned_data:
            username = self.cleaned_data['username']
            password = self.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(self.request, user)
                else:
                    raise forms.ValidationError(("This account is inactive"))
            else:
                raise forms.ValidationError((
                        "Username and/or password is incorrect"))

        if self.cleaned_data["remember_me"]:
            self.request.session.set_expiry(1000000)


class CreateUserForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    """
    user_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=("Username"),
                                error_messages={'invalid':
                                ("Username must contain only letters, numbers and underscores.")})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=("E-mail"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
        render_value=False), label=("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
        render_value=False), label=("Password (again)"))

    def clean_username(self):
        """
        Validate that the username is alphanumeric (for charfield only)
        and is not already in use.
        """
        try:
            User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError((
                "A user with that username already exists."))

    def clean_email(self):
        """
        Validate that the email is not already in use.
        """

        if User.objects.filter(
            email__iexact=self.cleaned_data['email']).exists():
            raise forms.ValidationError(("This email already exists"))
        else:
            return self.cleaned_data['email']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        non_field_errors() because it doesn't apply to a single
        field.
        """
        if 'password1' in self.cleaned_data and\
                'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data[
                'password2']:
                raise forms.ValidationError((
                        "The two password fields didn't match."))
        return self.cleaned_data

    def save_user(self):
        """
        Creates if new registration. Updates if user id is given
        """
        response = reply_object()
        try:
            if self.cleaned_data["user_id"] == 0 or\
                self.cleaned_data["user_id"] == u'' or\
                self.cleaned_data["user_id"] == None:
                response = self.create_user()
            else:
                response = self.update_user()
        except:
            response["code"] = settings.APP_CODE["SYSTEM ERROR"]

        return response

    def create_user(self):
        """
        Creates a new user
        """
        response = reply_object()
        new_user = User.objects.create(username=self.cleaned_data["username"],
                                       email=self.cleaned_data["email"])

        new_user.set_password(self.cleaned_data["password1"])
        if settings.EMAIL_VERIFICATION_REQUIRED:
            new_user.is_active = False
        else:
            new_user.is_active = True
        new_user.save()
        response["code"] = settings.APP_CODE["REGISTERED"]
        response["user_id"] = new_user.id
        return response

    def update_user(self):
        """
        Updates a registered user. Can be used for updating profile
        """
        response = reply_object()
        user = User.objects.get(pk=self.cleaned_data["user_id"])
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        user.save()
        response["code"] = settings.APP_CODE["UPDATED"]
        response["user_id"] = user.id
        return response


class PasswordEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        # check if email exists
        request_email = self.cleaned_data["email"]
        if not User.objects.filter(email=request_email).exists():
            raise forms.ValidationError(("This email does not exist"))

        # check if email is already used with 3rd part login
        if UserProfile.objects.filter(Q(facebook_email=request_email) |\
                                       Q(google_email=request_email)).exists():
            raise forms.ValidationError(("This email is already used with a social account please login via social login"))

        return self.cleaned_data["email"]

    def send_reset_link(self):
        response = reply_object()
        user = User.objects.get(email=self.cleaned_data["email"])
        if not user.is_active:
            response["code"] = settings.APP_CODE["SERVER MESSAGE"]
            response["server_message"] = "This account is inactive. Please contact site administrator"
            return response
        profile = user.get_profile()
        key_object = create_key(user.username, 2)
        profile.verification_key = key_object["key"]
        profile.key_expires = key_object["expiry"]
        send_password_reset_email(user.email, key_object["key"])
        profile.save()
        response["code"] = settings.APP_CODE["CALLBACK"]
        return response


class PasswordResetForm(forms.Form):
    """
    Password reset form
    """
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def clean(self):
        if 'password' in self.cleaned_data and 'confirm_password' in\
                self.cleaned_data:

            if self.cleaned_data["password"] !=\
                    self.cleaned_data["confirm_password"]:
                raise forms.ValidationError(("Passwords does not match"))
        return self.cleaned_data

    def save_new_password(self):
        response = reply_object()
        user = self.request.user
        user.set_password(self.cleaned_data['password'])
        user.save()
        response["code"] = settings.APP_CODE["CALLBACK"]
        return response
