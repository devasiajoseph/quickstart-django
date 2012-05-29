import sha
import random
import datetime
from django.core.mail import send_mail
from django.conf import settings


def send_activation_email(email, key):
    email_subject = 'Activate your account'
    email_body = 'Account activation Link %(site_url)sactivate/%(activation_key)s' % {"site_url": settings.SITE_URL, "activation_key": key}
    send_mail(email_subject,
              email_body,
              settings.ADMIN_EMAIL,
              [email],
              fail_silently=False)


def create_key(mixer, expiry):
    salt = sha.new(str(random.random())).hexdigest()[:10]
    key = sha.new(salt + mixer).hexdigest()
    key_expires = datetime.datetime.today() + datetime.timedelta(2)
    return {"key": key, "expiry": key_expires}


def reply_object():
    """
    reference for the reply json object
    """
    reply_object = {"code": ""}
    return reply_object
