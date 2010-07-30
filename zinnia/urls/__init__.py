"""Defaults urls for the zinnia project"""
from django.conf.urls.defaults import *
from zinnia.settings import ZINNIA_BLOG_PATTERN
from zinnia.settings import ZINNIA_BLOG_ACTIVE

urlpatterns = patterns('',
                       url(r'^tags/', include('zinnia.urls.tags',)),
                       url(r'^feeds/', include('zinnia.urls.feeds')),
                       url(r'^authors/', include('zinnia.urls.authors')),
                       url(r'^categories/', include('zinnia.urls.categories')),
                       url(r'^search/', include('zinnia.urls.search')),
                       url(r'^sitemap/', include('zinnia.urls.sitemap')),
                       url(r'^', include('zinnia.urls.capabilities')),
)

if ZINNIA_BLOG_ACTIVE:
    urlpatterns += patterns('',
                           url(r'^entries/', include('zinnia.urls.entries')),
                           url(r'^(?P<blog_slug>%s)/tags/' % ZINNIA_BLOG_PATTERN, include('zinnia.urls.tags',)),
                           url(r'^(?P<blog_slug>%s)/feeds/' % ZINNIA_BLOG_PATTERN, include('zinnia.urls.feeds')),
                           url(r'^(?P<blog_slug>%s)/authors/' % ZINNIA_BLOG_PATTERN, include('zinnia.urls.authors')),
                           url(r'^(?P<blog_slug>%s)/categories/' % ZINNIA_BLOG_PATTERN, include('zinnia.urls.categories')),
                           url(r'^(?P<blog_slug>%s)/search/' % ZINNIA_BLOG_PATTERN, include('zinnia.urls.search')),
                           url(r'^(?P<blog_slug>%s)/sitemap/' % ZINNIA_BLOG_PATTERN, include('zinnia.urls.sitemap')),
                           url(r'^(?P<blog_slug>%s)/entries/' % ZINNIA_BLOG_PATTERN, include('zinnia.urls.entries')), 
                           url(r'^', include('zinnia.urls.blogs')),
    )
else:
    urlpatterns += patterns('',
                           url(r'^', include('zinnia.urls.entries')),
    )

