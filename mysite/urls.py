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
    url(r'^$', 'core.views.index', name='index'),
    url(r'^home$', 'core.views.home', name='home'),
    url(r'^login/$', 'core.views.user_login', name='login'),
    url(r'^login_user$', 'core.views.login_user', name='login_user'),
    url(r'^logout', 'core.views.user_logout', name='logout'),
    url(r'^register', 'core.views.user_register', name='register'),
    url(r'^add/user$', 'core.views.add_user'),
    url(r'^activate/(?P<verification_key>[0-9a-z]+)$', 'core.views.activate'),
    url(r'^registration/success$', 'core.views.registration_success',
        name='registration_success'),
    #Facebook urls
    url(r'^start/fbauth', 'core.views.start_fbauth', name='start_fbauth'),
    url(r'^fbauth', 'core.views.fbauth', name='fbauth'),
    #twitter urls
    url(r'^start/twauth', 'core.views.start_twauth', name='start_twauth'),
    url(r'^twauth', 'core.views.twauth', name='twauth'),
    #google urls
    url(r'^start/googleauth', 'core.views.start_googleauth',
        name='start_googleauth'),
    url(r'^oauth2callback', 'core.views.googleauth', name='googleauth'),
    #password reset
    url(r'^password/reset$', 'core.views.password_reset',
        name='password_reset'),
    url(r'^password/reset/submit/email$',
        'core.views.password_reset_submit_email',
        name='password_reset_submit_email'),
    url(r'^password/reset/form/(?P<verification_key>[0-9a-z]+)$',
        'core.views.password_reset_form',
        name='password_reset_form'),
    url(r'^password/reset/submit/password$',
        'core.views.password_reset_submit_password',
        name='password_reset_submit_password'),
    #test url
    url(r'^test$', 'core.views.test', name='test'),
)
