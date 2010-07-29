"""Urls for the zinnia categories"""
from django.conf.urls.defaults import *

from zinnia.models import Category

urlpatterns = patterns('zinnia.views.categories',
                        url(r'^$', 'category_list', {}, 'zinnia_category_list'),
                        url(r'^(?P<slug>[-\w]+)/$', 'category_detail', 
                            name='zinnia_category_detail'),
                        url(r'^(?P<slug>[-\w]+)/page/(?P<page>\d+)/$',
                            'category_detail',
                            name='zinnia_category_detail_paginated'),
                        )
