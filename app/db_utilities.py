from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


def create_new_user(username, password, email, first_name="", last_name=""):
    new_user = User.objects.create(username=username,
                                   email=email,
                                   first_name=first_name,
                                   last_name=last_name)

    new_user.set_password(password)
    new_user.save()
    return new_user


def third_party_login(username, password, request, email=""):
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
    else:
        user = create_new_user(username, password, email)

    user_auth = authenticate(username=user.username, password=password)
    if user_auth is not None:
        login(request, user_auth)

    return user
