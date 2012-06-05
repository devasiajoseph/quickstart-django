from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from app.utilities import send_activation_email, create_key
from django.conf import settings
from django.core.context_processors import csrf
from app.facebooksdk import Facebook
import requests
import re
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
import simplejson
from twython import Twython
from oauth2client.client import OAuth2WebServerFlow


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    verification_key = models.CharField(max_length=1024)
    key_expires = models.DateTimeField(null=True)
    location = models.CharField(max_length=255)
    home_town = models.CharField(max_length=255)
    gender = models.CharField(max_length=1024)
    facebook_id = models.CharField(max_length=100)
    facebook_username = models.CharField(max_length=100)
    facebook_email = models.CharField(max_length=100)
    twitter_username = models.CharField(max_length=100)
    twitter_id = models.CharField(max_length=100)
    google_username = models.CharField(max_length=100)
    google_id = models.CharField(max_length=100)
    google_email = models.CharField(max_length=100)
    time_zone = models.CharField(max_length=100)


def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal for creating a new profile and setting activation key
    """

    if created:
        profile = UserProfile.objects.create(user=instance)

        if settings.EMAIL_VERIFICATION_REQUIRED:
            key_object = create_key(instance.username, 2)
            profile.verification_key = key_object["key"]
            profile.key_expires = key_object["expiry"]
            send_activation_email(instance.email, key_object["key"])

        profile.save()
    return

# connect to the signal
post_save.connect(create_user_profile, sender=User)


class SocialAuth(object):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.username = ""
        self.password = ""
        self.first_name = ""
        self.last_name = ""
        self.email = ""
        self.home_town = ""
        self.location = ""
        self.gender = ""
        self.user = kwargs.pop("user", None)

        super(SocialAuth, self).__init__(*args, **kwargs)

    def create_new_user(self):
        new_user = User.objects.create(username=self.username,
                                       email=self.email,
                                       first_name=self.first_name,
                                       last_name=self.last_name)

        new_user.set_password(self.password)
        new_user.save()
        return new_user

    def social_login(self):
        if User.objects.filter(username=self.username).exists():
            user = User.objects.get(username=self.username)
            user.set_password(self.password)
            user.save()
        else:
            user = self.create_new_user()

        user_auth = authenticate(username=user.username,
                                 password=self.password)

        if user_auth is not None:
            login(self.request, user_auth)

        return user

    def facebook_step1(self):
        csrf_token = csrf(self.request)["csrf_token"]
        fbauth_dialog = settings.FBAPP_AUTH_REDIRECT % \
        {"FBAPP_ID": settings.FBAPP_ID,
         "FBAPP_REDIRECT_URI": settings.FBAPP_REDIRECT_URI,
         "SCOPE": "email",
         "CSRF_TOKEN": csrf_token}

        return fbauth_dialog

    def facebook_step2(self):
        fbauth_token_url = settings.FBAPP_ACCESS_TOKEN_URL % \
            {"FBAPP_ID": settings.FBAPP_ID,
             "FBAPP_REDIRECT_URI": settings.FBAPP_REDIRECT_URI,
             "FBAPP_SECRET": settings.FBAPP_SECRET,
             "FB_CODE": self.request.GET["code"]}

        r = requests.get(fbauth_token_url)
        access_token = re.findall(
            "access_token=[a-zA-Z0-9]+", r.text)[0].replace(
            'access_token=', ""
            )
        facebook = Facebook()
        facebook.access_token = access_token
        facebook_user = facebook.user_info()
        print facebook_user

        self.username = "facebook_" + facebook_user["username"]
        self.password = access_token
        self.email = facebook_user["email"]

        facebook_social_user = self.facebook_login(facebook_user)
        return facebook_social_user

    def facebook_login(self, fb_user):
        logged_in_user = self.social_login()
        facebook_profile = logged_in_user.get_profile()
        facebook_profile.first_name = fb_user["first_name"]
        facebook_profile.last_name = fb_user["last_name"]
        facebook_profile.home_town = fb_user["home_town"]["name"]
        facebook_profile.location = fb_user["location"]["name"]
        facebook_profile.gender = fb_user["gender"]
        facebook_profile.facebook_username = facebook_user["username"]
        facebook_profile.facebook_id = facebook_user["id"]
        facebook_profile.save()
        return True

    def twitter_step1(self):
        # Instantiate Twython with the first leg of our trip.
        twitter = Twython(twitter_token=settings.TWITTER_KEY,
                          twitter_secret=settings.TWITTER_SECRET,
                          callback_url=settings.SITE_URL + reverse('twauth'))

        # Request an authorization url to send the user to...
        auth_props = twitter.get_authentication_tokens()

        # Then send them over there, durh.
        self.request.session['request_token'] = auth_props

        return auth_props['auth_url']

    def twitter_step2(self):
        # Instantiate Twython with the authernticated tokens
        twitter = Twython(
        twitter_token=settings.TWITTER_KEY,
        twitter_secret=settings.TWITTER_SECRET,
        oauth_token=self.request.session['request_token']['oauth_token'],
        oauth_token_secret=self.request.session[
                'request_token']['oauth_token_secret']
        )

        # Retrieve the tokens we want...
        authorized_tokens = twitter.get_authorized_tokens()
        print authorized_tokens
        r = requests.get(
          "http://api.twitter.com/1/users/lookup.json?user_id=%s" % \
              authorized_tokens["user_id"])
        d = simplejson.loads(r.text)
        twitter_user = d[0]
        self.username = authorized_tokens["screen_name"]
        self.password = authorized_tokens["oauth_token"]
        return self.twitter_login(twitter_user)

    def twitter_login(self, tw_user):
        logged_in_user = self.social_login()
        twitter_profile = logged_in_user.get_profile()
        twitter_profile.twitter_username = tw_user["screen_name"]
        twitter_profile.twitter_id = tw_user["id_str"]
        twitter_profile.first_name = tw_user["name"].split(" ")[0]
        twitter_profile.last_name = tw_user["name"].split(" ")[1]
        twitter_profile.location = tw_user["location"]
        twitter_profile.save()
        return True

    def google_step1(self):
        flow = OAuth2WebServerFlow(
        # Visit https://code.google.com/apis/console to
        # generate your client_id, client_secret and to
        # register your redirect_uri.
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_SECRET,
        scope=['profile', 'email'],
        user_agent=self.request.META["HTTP_USER_AGENT"],
        redirect_uri=settings.GOOGLE_REDIRECT_URI)

        callback = settings.GOOGLE_REDIRECT_URI
        authorize_url = flow.step1_get_authorize_url(callback)
        return authorize_url

    def google_step2(self):
        flow = OAuth2WebServerFlow(
        # Visit https://code.google.com/apis/console to
        # generate your client_id, client_secret and to
        # register your redirect_uri.
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_SECRET,
        scope=['profile', 'email'],
        user_agent=self.request.META["HTTP_USER_AGENT"],
        redirect_uri=settings.GOOGLE_REDIRECT_URI)
        credential = flow.step2_exchange(self.request.REQUEST)
        r = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token="\
            + credential.access_token)
        d = simplejson.loads(r.text)
        self.username = "google_" + d["email"].split("@")[0]
        self.password = credential.access_token
        self.email = d["email"]
        return self.google_login(d)

    def google_login(self, google_user):
        logged_in_user = self.social_login()
        google_profile = logged_in_user.get_profile()
        google_profile.first_name = google_user["name"].split(" ")[0]
        google_profile.last_name = google_user["name"].split(" ")[1]
        google_profile.gender = google_user["gender"]
        google_profile.save()
        return True
