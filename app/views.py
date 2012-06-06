# Create your views here.
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from app.forms import CreateUserForm, LoginForm
from app.utilities import reply_object
import simplejson
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
import datetime
from django.shortcuts import get_object_or_404
from app.models import UserProfile, SocialAuth
from app.forms import PostForm


def index(request):
    print settings.SITE_URL + reverse('twauth')
    return render_to_response("index.html",
                              context_instance=RequestContext(request))


def home(request):
    """
    Home page after logging in
    """
    if request.user.is_authenticated():
        return render_to_response("home.html",
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('login'))


def user_register(request):
    """
    Registration page
    """
    form = CreateUserForm()
    return render_to_response(
        "register.html",
        context_instance=RequestContext(request, {"user_form": form}))


def add_user(request):
    """
    Registration request handler
    """
    response = reply_object()
    form = CreateUserForm(request.POST)
    if form.is_valid():
        response = form.save_user()
        response["success_page"] = reverse('registration_success')
    else:
        response["code"] = settings.APP_CODE["FORM ERROR"]
        response["errors"] = form.errors
    return HttpResponse(simplejson.dumps(response))


def registration_success(request):
    return render_to_response('registration_success.html',
                              context_instance=RequestContext(request,
                {"activation_email": settings.EMAIL_VERIFICATION_REQUIRED}))


def user_login(request):
    """
    Login page
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    form = LoginForm(request=request)
    return render_to_response("login.html",
            context_instance=RequestContext(request,
                {"login_form": form}))


def login_user(request):
    """
    Login request handler
    """
    response = reply_object()
    form = LoginForm(request.POST, request=request)

    if form.is_valid():
        response["code"] = settings.APP_CODE["LOGIN"]
        response["next_view"] = reverse('home')
    else:
        response["code"] = settings.APP_CODE["FORM ERROR"]
        response["errors"] = form.errors

    return HttpResponse(simplejson.dumps(response))


def user_logout(request):
    """
    Logout request
    """
    # Logout function flushes all sessions.Save session variables to a local
    # variable for reuse
    logout(request)
    return HttpResponseRedirect(reverse('login'))


def activate(request, activation_key):
    """
    New account activation function
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    naive_date = user_profile.key_expires.replace(tzinfo=None)
    if naive_date < datetime.datetime.today():
        return render_to_response('expired.html',
                                  context_instance=RequestContext(request))
    user_account = user_profile.user
    user_account.is_active = True
    user_account.save()
    #remove activation key once account is activated
    user_profile.activation_key = ""
    user_profile.save()
    return render_to_response('activated.html',
                              context_instance=RequestContext(request))


def start_fbauth(request):
    """
    Starting point for facebook authentication
    """
    social_auth = SocialAuth(request=request)
    redirect_url = social_auth.facebook_step1()
    return HttpResponseRedirect(redirect_url)


def fbauth(request):
    """
    Redirect function after facebook authentication
    """
    social_auth = SocialAuth(request=request)
    social_auth.facebook_step2()
    return HttpResponseRedirect(reverse('home'))


def start_twauth(request):
    """
        The view function that initiates the entire handshake.
    """
    social_auth = SocialAuth(request=request)
    redirect_url = social_auth.twitter_step1()
    return HttpResponseRedirect(redirect_url)


def twauth(request):
    """
    Redirect function after twitter login
    """

    social_auth = SocialAuth(request=request)
    social_auth.twitter_step2()
    return HttpResponseRedirect(reverse('home'))


def start_googleauth(request):
    """
    Starting point for google authentication
    uses oauth2.0
    """
    social_auth = SocialAuth(request=request)
    redirect_url = social_auth.google_step1()
    return HttpResponseRedirect(redirect_url)


def googleauth(request):
    social_auth = SocialAuth(request=request)
    social_auth.google_step2()
    return HttpResponseRedirect(reverse('home'))


def test(request):
    """
    Test function
    """
    print "test"
    return HttpResponse("test")
