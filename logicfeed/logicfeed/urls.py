from django.conf.urls import patterns, include, url
from django.contrib import admin

from console.views import PostView


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'logicfeed.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', PostView.as_view(), name='post'),
    url(r'^fetch/$', 'console.views.fetch', name='fetch'),
)
