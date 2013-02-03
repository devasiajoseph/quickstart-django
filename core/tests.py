"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
#from adserver.test.mongotest import AdServerTestCase
from django.test.client import Client
from django.conf import settings
import simplejson
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


def logged_in_client(username=settings.APP_USERNAME,
        password=settings.APP_PASSWORD):
    c = Client()
    c.login(username=username, password=password)
    return c


def check_url_access(url, is_ajax=False, post_required=False):
    access_parameters = {}
    c = Client()
    if is_ajax:
        response = c.get(url, **{'HTTP_X_REQUESTED_WITH':
            'XMLHttpRequest'})
        parsed_data = simplejson.loads(response.content)
        if parsed_data["code"] == settings.APP_CODE["ACCESS DENIED"]:
            access_parameters["ajax_valid"] = True
            access_parameters["ajax_message"] = ""
        else:
            access_parameters["ajax_valid"] = False
            access_parameters["ajax_message"] =\
                'Ajax access error:%s can be accessed without logging in' % url

    if post_required:
        lc = logged_in_client()
        response = lc.get(url)
        if response.status_code == 302 and reverse('invalid_request') in\
                response['Location']:
            access_parameters["post_valid"] = True
            access_parameters["post_message"] = ""
        else:
            access_parameters["post_valid"] = False
            access_parameters["post_message"] =\
                'Post data error:%s can be accessed without post data' % url

    response = c.get(url)
    if response.status_code == 302 and (reverse('access_denied') in \
            response['Location'] or reverse('login') in response['Location']):
        access_parameters["valid"] = True
        access_parameters["message"] = ""
    else:
        access_parameters["valid"] = False
        access_parameters["message"] =\
            'Security access error:%s can be accessed without logging in' % url

    return access_parameters


def verify_json_response(string_data, code):
    data = simplejson.loads(string_data)
    if data["code"] == code:
        return True
    else:
        return False
