from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'reg.views.home', name='home'),
    # url(r'^reg/', include('reg.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'app.views.index', name='index'),
    url(r'^home$', 'app.views.home', name='home'),
    url(r'^login/$', 'app.views.user_login', name='login'),
    url(r'^login_user$', 'app.views.login_user', name='login_user'),
    url(r'^logout', 'app.views.user_logout', name='logout'),
    url(r'^register', 'app.views.user_register', name='register'),
    url(r'^add/user$', 'app.views.add_user'),
    url(r'^activate/(?P<activation_key>[0-9a-z]+)$', 'app.views.activate'),
    url(r'^registration/success$', 'app.views.registration_success',
        name='registration_success'),
    #Facebook urls
    url(r'^start/fbauth', 'app.views.start_fbauth', name='start_fbauth'),
    url(r'^fbauth', 'app.views.fbauth', name='fbauth'),
    #twitter urls
    url(r'^start/twauth', 'app.views.start_twauth', name='start_twauth'),
    url(r'^twauth', 'app.views.twauth', name='twauth'),
    #google urls
    url(r'^start/googleauth', 'app.views.start_googleauth',
        name='start_googleauth'),
    url(r'^oauth2callback', 'app.views.googleauth', name='googleauth'),
    #password reset
    url(r'^password/reset$', 'app.views.password_reset',
        name='password_reset'),
    #test url
    url(r'^test$', 'app.views.test', name='test'),
)
