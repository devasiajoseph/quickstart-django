APP_USERNAME = "dev"
APP_PASSWORD = "password"

ADMIN_EMAIL = "admin@site.com"
SITE_URL = "http://yoursiteurl"
EMAIL_USE_TLS = True  # True for gmail testing
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587  # 587 for gmail server
EMAIL_VERIFICATION_REQUIRED = False
FBAPP_ID = ""
FBAPP_SECRET = ""
FBAPP_REDIRECT_URI = "http://yoursite/fbauth"


FBAPP_AUTH_REDIRECT = "https://www.facebook.com/dialog/oauth?\
client_id=%(FBAPP_ID)s&\
redirect_uri=%(FBAPP_REDIRECT_URI)s&\
&state=%(CSRF_TOKEN)s"

FBAPP_ACCESS_TOKEN_URL = "https://graph.facebook.com/oauth/access_token?\
client_id=%(FBAPP_ID)s\
&redirect_uri=%(FBAPP_REDIRECT_URI)s&\
client_secret=%(FBAPP_SECRET)s&\
code=%(FB_CODE)s"

TWITTER_KEY = ''
TWITTER_SECRET = ''

GOOGLE_AUTH_REDIRECT = "https://accounts.google.com/o/oauth2/auth?redirect_uri=https://localhost/oauth2callback&response_type=code&client_id=56279468910.apps.googleusercontent.com&approval_prompt=force&scope=https://Fwww.googleapis.com/Fauth/blogger&access_type=offline"

GOOGLE_SECRET = ""
GOOGLE_CLIENT_ID = ""
