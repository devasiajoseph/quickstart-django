# Create your views here.
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from app.forms import CreateUserForm, LoginForm, FacebookLoginForm
from app.utilities import reply_object
import simplejson
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
import datetime
from django.shortcuts import get_object_or_404
from app.models import UserProfile
from django.core.context_processors import csrf
from twython import Twython
from app.db_utilities import third_party_login


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
    csrf_token = csrf(request)["csrf_token"]
    fbauth_dialog = settings.FBAPP_AUTH_REDIRECT % \
        {"FBAPP_ID": settings.FBAPP_ID,
         "FBAPP_REDIRECT_URI": settings.FBAPP_REDIRECT_URI,
         "CSRF_TOKEN": csrf_token}
    return HttpResponseRedirect(fbauth_dialog)


def fbauth(request):
    """
    Redirect function after facebook authentication
    """
    form = FacebookLoginForm(request.GET, request=request)
    if form.is_valid():
        user = form.facebook_login()
    return HttpResponseRedirect(reverse('home'))


def start_twauth(request):
    """
        The view function that initiates the entire handshake.
        For the most part, this is 100% drag and drop.
    """
    # Instantiate Twython with the first leg of our trip.
    twitter = Twython(twitter_token=settings.TWITTER_KEY,
                  twitter_secret=settings.TWITTER_SECRET,
                  callback_url=request.build_absolute_uri(reverse('twauth'))
                  )

    # Request an authorization url to send the user to...
    auth_props = twitter.get_authentication_tokens()

    # Then send them over there, durh.
    request.session['request_token'] = auth_props
    return HttpResponseRedirect(auth_props['auth_url'])


def twauth(request):
    """
    Redirect function after twitter login
    """
    # Instantiate Twython with the authernticated tokens
    twitter = Twython(
    twitter_token=settings.TWITTER_KEY,
    twitter_secret=settings.TWITTER_SECRET,
    oauth_token=request.session['request_token']['oauth_token'],
    oauth_token_secret=request.session['request_token']['oauth_token_secret'],
    )

    # Retrieve the tokens we want...
    authorized_tokens = twitter.get_authorized_tokens()
    user = third_party_login("twitter_" + authorized_tokens["screen_name"],
            authorized_tokens["oauth_token"],
            request)
    return HttpResponseRedirect(reverse('home'))
