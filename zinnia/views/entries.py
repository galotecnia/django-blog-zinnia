"""Views for zinnia entries"""
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import object_detail
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day
from django.shortcuts import get_object_or_404

from zinnia.models import Entry
from zinnia.models import Blog
from zinnia.views.decorators import update_queryset
from django.contrib.comments.views.comments import post_comment
from django.contrib.comments.views.comments import comment_done

entry_index = update_queryset(object_list, Entry.published.all)

entry_year = update_queryset(archive_year, Entry.published.all)

entry_month = update_queryset(archive_month, Entry.published.all)

entry_day = update_queryset(archive_day, Entry.published.all)

entry_detail = update_queryset(object_detail, Entry.published.all)

def zinnia_post_comment(request, blog_slug):
    """Post comment wrapper, add blog_slug to context"""
    blog = get_object_or_404(Blog, slug = blog_slug)
    request.session['blog'] = blog
    return post_comment(request)

def zinnia_comment_done(request, blog_slug):
    """Comment done wrapper, add blog_slug to context"""
    blog = get_object_or_404(Blog, slug = blog_slug)
    request.session['blog'] = blog
    return comment_done(request)
