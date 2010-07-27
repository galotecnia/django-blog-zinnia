from django.conf.urls.defaults import *

from zinnia.models import Entry, Blog
from zinnia.settings import PAGINATION
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_year, archive_month, archive_day, object_detail
from zinnia.managers import entries_published
from django.shortcuts import get_object_or_404

blog_index =   {'queryset': Blog.objects.all(),
                'paginate_by': PAGINATION,
                'template_name': 'zinnia/blog_list.html',
                'extra_context': {'default_list': True, 'read_more': True},
               }

blog_index_no_content = {'queryset': Blog.objects.all(),
                'paginate_by': PAGINATION,
                'template_name': 'zinnia/blog_list.html',
                'extra_context': {'default_list': False, 'read_more': True},
               }

urlpatterns = patterns('',
                        url(r'^$', object_list, blog_index, name='blogs'),                  
                        url(r'^list/', object_list, blog_index_no_content, name='blog_list'), 
                        )
