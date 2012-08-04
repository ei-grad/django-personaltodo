from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'personaltodo.views.home', name='home'),
    url(r'^search/$', 'personaltodo.views.search', name='search'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('todo.urls')),
)
