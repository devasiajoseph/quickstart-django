from django import forms
from django.conf import settings
from app.utilities import reply_object
from app.db_utilities import create_new_user, third_party_login
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import requests
import re
from facebooksdk import Facebook

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
                raise forms.ValidationError(("Username and/or password is incorrect"))

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
        raise forms.ValidationError(("A user with that username already exists."))

    def clean_email(self):
        """
        Validate that the email is not already in use.
        """

        try:
            User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(("This email already exists"))

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        non_field_errors() because it doesn't apply to a single
        field.
        """
        if 'password1' in self.cleaned_data and\
                'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(("The two password fields didn't match."))
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


class FacebookLoginForm(forms.Form):
    code = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FacebookLoginForm, self).__init__(*args, **kwargs)

    def facebook_login(self):
        fbauth_token_url = settings.FBAPP_ACCESS_TOKEN_URL % \
            {"FBAPP_ID": settings.FBAPP_ID,
             "FBAPP_REDIRECT_URI": settings.FBAPP_REDIRECT_URI,
             "FBAPP_SECRET": settings.FBAPP_SECRET,
             "FB_CODE": self.cleaned_data["code"]}

        r = requests.get(fbauth_token_url)
        access_token = re.findall(
            "access_token=[a-zA-Z0-9]+", r.text)[0].replace(
            'access_token=', ""
            )
        facebook = Facebook()
        facebook.access_token = access_token
        facebook_user = facebook.user_info()
        print facebook_user
        user = third_party_login("facebook_" + facebook_user["username"],
            access_token,
            self.request)
