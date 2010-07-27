"""Defaults urls for the zinnia project"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^tags/', include('zinnia.urls.tags',)),
                       url(r'^feeds/', include('zinnia.urls.feeds')),
                       url(r'^authors/', include('zinnia.urls.authors')),
                       url(r'^categories/', include('zinnia.urls.categories')),
                       url(r'^search/', include('zinnia.urls.search')),
                       url(r'^sitemap/', include('zinnia.urls.sitemap')),
                       url(r'^', include('zinnia.urls.blogs')),
                       url(r'^', include('zinnia.urls.entries')),
                       url(r'^', include('zinnia.urls.capabilities')),
                       )

