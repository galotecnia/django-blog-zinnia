"""Urls for the zinnia entries"""
from django.conf.urls.defaults import *

from zinnia.models import Entry
from zinnia.models import Blog
from zinnia.settings import PAGINATION
from zinnia.settings import ALLOW_EMPTY
from zinnia.settings import ALLOW_FUTURE


entry_conf_list = {'queryset': Entry.published.all(),
                   'paginate_by': PAGINATION,}

entry_conf = {'queryset': Entry.published.all(),
              'date_field': 'creation_date',
              'allow_empty': ALLOW_EMPTY,
              'allow_future': ALLOW_FUTURE,
              'month_format': '%m'}

entry_conf_year = entry_conf.copy()
entry_conf_year['make_object_list'] = True
del entry_conf_year['month_format']

entry_conf_detail = entry_conf.copy()
del entry_conf_detail['allow_empty']
entry_conf_detail['queryset'] = Entry.objects.all()

# Entries group
urlpatterns = patterns('zinnia.views.entries',
                    url(r'^$', 'entry_index', entry_conf_list,
                       name='zinnia_entry_archive_index'),
                    url(r'^page/(?P<page>\d+)/$', 'entry_index', entry_conf_list,
                       name='zinnia_entry_archive_index_paginated'),
                    url(r'^(?P<year>\d{4})/$', 'entry_year',
                       entry_conf_year, name='zinnia_entry_archive_year'),
                    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', 'entry_month',
                       entry_conf, name='zinnia_entry_archive_month'),
                    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'entry_day',
                       entry_conf, name='zinnia_entry_archive_day'),
                    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
                        'entry_detail', entry_conf_detail, name='zinnia_entry_detail'),
                    url(r'^comments/post/$',    'zinnia_post_comment', name='post_comment'),
                    url(r'^comments/posted/$',  'zinnia_comment_done', name='comments-comment-done'),

)
