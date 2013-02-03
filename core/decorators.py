from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from app.utilities import reply_object
from functools import wraps
import simplejson


def check_access(request, permission):
    """
    Checks defined access
    """
    access_parameters = reply_object()
    access_parameters["redirect_url"] = "access_denied"
    access_parameters["allow_access"] = False
    if not request.user.is_authenticated():
        access_parameters["redirect_url"] = "login"
        return access_parameters
    if permission == "user":
        access_parameters["allow_access"] = True
        return access_parameters
    if permission == "admin":
        me = request.user
        if me.is_superuser:
            access_parameters["allow_access"] = True
    if permission == "client":
        me = request.user
        if me.is_staff or me.is_superuser:
            access_parameters["allow_access"] = True

        return access_parameters

    return access_parameters


def post_required(view_func):
    """
    Decorator for views that checks that data is submitted to the view
    """
    def _checkpost(request, *args, **kwargs):
        """
        Checks for post data
        """
        response_object = {}
        if request.method == "POST":
            return view_func(request, *args, **kwargs)
        else:
            if request.is_ajax():
                response_object["code"] = settings.\
                            APP_CODE["INVALID REQUEST"]
                return HttpResponse(simplejson.dumps(response_object))
            else:
                return HttpResponseRedirect(
                    reverse("invalid_request"))
    return wraps(view_func)(_checkpost)


def tag_processor(view_func):
    """
    Decorator for views has tag handling
    """
    def _check_tag_query(request, *args, **kwargs):
        """
        checks tag queries
        """
        if "addtag" in request.GET:
            return HttpResponseRedirect("/news/tags/?addtag=" + \
                request.GET["addtag"])
        else:
            return view_func(request, *args, **kwargs)

    return wraps(view_func)(_check_tag_query)


def access_required(permission, next_view=None):
    """
    Checks user access to a particular view
    Redirects to login if a page is requested
    Adds access denied code if ajax request
    """
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            access_parameters = check_access(request, permission)
            if access_parameters["allow_access"]:
                return func(request, *args, **kwargs)
            else:
                if request.is_ajax():
                    access_parameters["code"] = settings.\
                            APP_CODE["ACCESS DENIED"]
                    access_parameters["success"] = False
                    return HttpResponse(simplejson.dumps(access_parameters))
                else:
                    request.session['next_view'] = request.get_full_path()
                    return HttpResponseRedirect(
                        reverse(access_parameters["redirect_url"]))

        return wraps(func)(inner_decorator)

    return decorator
