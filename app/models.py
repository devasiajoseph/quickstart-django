from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from app.utilities import send_activation_email, create_key
from django.conf import settings
from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    verification_key = models.CharField(max_length=1024)
    key_expires = models.DateTimeField()
    facebook_id = models.CharField(max_length=100)
    facebook_username = models.CharField(max_length=100)
    twitter_username = models.CharField(max_length=100)
    twitter_id = models.CharField(max_length=100)


class FlowModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    flow = FlowField()


class CredentialsModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    credential = CredentialsField()


def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal for creating a new profile and setting activation key
    """
    if not settings.EMAIL_VERIFICATION_REQUIRED:
        return
    if created:
        key_object = create_key(instance.username, 2)
        UserProfile.objects.create(user=instance,
                                   verification_key=key_object["key"],
                                   key_expires=key_object["expiry"])

        send_activation_email(instance.email, key_object["key"])

# connect to the signal
post_save.connect(create_user_profile, sender=User)
