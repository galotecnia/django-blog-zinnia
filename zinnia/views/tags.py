"""Views for zinnia tags"""
from django.views.generic.list_detail import object_list
from django.shortcuts import get_object_or_404
from tagging.views import tagged_object_list

from zinnia.models import Entry
from zinnia.models import Blog
from zinnia.managers import tags_published
from zinnia.views.decorators import update_queryset
from zinnia.settings import ZINNIA_BLOG_ACTIVE

def tag_list(request, **kwargs):
    """Display the general tag list or blog's tag list"""
    if ZINNIA_BLOG_ACTIVE:
        blog_slug = kwargs.pop('blog_slug')
        blog = get_object_or_404(Blog, slug = blog_slug)
        kwargs['queryset'] = tags_published(blog_slug)
        kwargs['extra_context'] = {'blog': blog}
    return object_list(request, **kwargs)

tag_detail = update_queryset(tagged_object_list, Entry.published.all,
                             'queryset_or_model')
