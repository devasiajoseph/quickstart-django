import base64
import json
import hmac
import hashlib
import time
import requests
from django.conf import settings
"""
    Users: https://graph.facebook.com/btaylor (Bret Taylor)
    Pages: https://graph.facebook.com/cocacola (Coca-Cola page)
    Events: https://graph.facebook.com/251906384206 (EventID)
    Groups: https://graph.facebook.com/195466193802264
    Applications: https://graph.facebook.com/2439131959 (the Graffiti app)
    Status messages: https://graph.facebook.com/367501354973
    Photos: https://graph.facebook.com/98423808305
    Photo albums: https://graph.facebook.com/99394368305
    Profile pictures: http://graph.facebook.com/devasiajoseph/picture
    Videos: https://graph.facebook.com/817129783203
    Notes: https://graph.facebook.com/122788341354
    Checkins: https://graph.facebook.com/414866888308 (Check-in at a pizzeria)

    Friends: https://graph.facebook.com/me/friends?access_token=...
    News feed: https://graph.facebook.com/me/home?access_token=...
    Profile feed (Wall): https://graph.facebook.com/me/feed?access_token=...
    Likes: https://graph.facebook.com/me/likes?access_token=...
    Movies: https://graph.facebook.com/me/movies?access_token=...
    Music: https://graph.facebook.com/me/music?access_token=...
    Books: https://graph.facebook.com/me/books?access_token=...
    Notes: https://graph.facebook.com/me/notes?access_token=...
    Permissions: https://graph.facebook.com/me/permissions?access_token=...
    Photo Tags: https://graph.facebook.com/me/photos?access_token=...
    Photo Albums: https://graph.facebook.com/me/albums?access_token=...
    Video Tags: https://graph.facebook.com/me/videos?access_token=...
    Video Uploads: https://graph.facebook.com/me/videos/uploaded?access_token=
    Events: https://graph.facebook.com/me/events?access_token=...
    Groups: https://graph.facebook.com/me/groups?access_token=...
    Checkins: https://graph.facebook.com/me/checkins?access_token=...

"""


class OfflineFacebook(object):
    def __init__(self):
        self.app_id = settings.FBAPP_ID
        self.app_secret = settings.FBAPP_SECRET
        self.graph_url = "https://graph.facebook.com/"
        self.q = None

    def search(self):
        return


class Facebook(object):
    def __init__(self):
        self.app_id = settings.FBAPP_ID
        self.app_secret = settings.FBAPP_SECRET
        self.user_id = None
        self.access_token = None
        self.signed_request = {}
        self.graph_url = "https://graph.facebook.com/"

    def api(self, method='GET', param=''):
        if method == 'GET':
            r = requests.get('https://graph.facebook.com/me/%s' % param)
            data = json.loads(r.text)
            return data

        return data

    def user_info(self, method='GET', param=''):
        if method == 'GET':
            r = requests.get(
                'https://graph.facebook.com/me/%s?access_token=%s' % (
                    param, self.access_token))
            data = json.loads(r.text)
        return data

    @staticmethod
    def base64_url_decode(data):
        data = data.encode(u'ascii')
        data += '=' * (4 - (len(data) % 4))
        return base64.urlsafe_b64decode(data)

    @staticmethod
    def base64_url_encode(data):
        return base64.urlsafe_b64encode(data).rstrip('=')

    def load_signed_request(self, signed_request):
        """Load the user state from a signed_request value"""
        try:
            sig, payload = signed_request.split(u'.', 1)
            sig = self.base64_url_decode(sig)
            data = json.loads(self.base64_url_decode(payload))

            expected_sig = hmac.new(
                self.app_secret,
                msg=payload,
                digestmod=hashlib.sha256).digest()

            # allow the signed_request to function for upto 1 day
            if sig == expected_sig and \
                    data[u'issued_at'] > (time.time() - 86400):
                self.signed_request = data
                self.user_id = data.get(u'user_id')
                self.access_token = data.get(u'oauth_token')
        except:
            # ignore if can't split on dot
            print "exception"
            pass

    def api_bkp(self):
        r = requests.get('https://graph.facebook.com/%s/' % self.user_id)
        data = json.loads(r.text)
        return data

    def wall_post(self, message):
        r = requests.post(
            'https://graph.facebook.com/%s/feed' % self.user_id,
            data={"access_token": self.access_token,
                  "message": message})
        print r.text
