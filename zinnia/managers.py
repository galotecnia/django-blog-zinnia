"""Managers of Zinnia"""
from datetime import datetime

from django.db import models
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404

from zinnia.settings import ZINNIA_BLOG_ACTIVE

DRAFT = 0
HIDDEN = 1
PUBLISHED = 2

def get_filter(slug):
    """Check blog slug if necessary"""
    from zinnia.models import Blog
    if ZINNIA_BLOG_ACTIVE:
        blog = get_object_or_404(Blog, slug = slug)
        return {'blog__slug': slug}
    return {}

def tags_published(blog_slug = ''):
    """Return the pusblished tags"""
    from tagging.models import Tag
    from zinnia.models import Entry

    filter = get_filter(blog_slug)
    tags_published = Tag.objects.usage_for_queryset(Entry.published.filter(**filter))
    return Tag.objects.filter(name__in=[t.name for t in tags_published])

def authors_published(blog_slug = ''):
    """Return the published authors"""
    from django.contrib.auth.models import User
    from zinnia.models import Entry
    filter = {'entry__status': PUBLISHED}
    if ZINNIA_BLOG_ACTIVE:
        filter.update({'entry__blog__slug': blog_slug})
    return User.objects.filter(**filter).distinct()


def entries_published(queryset): 
    """Return only the entries published"""
    now = datetime.now()
    return queryset.filter(status=PUBLISHED,
                           start_publication__lte=now,
                           end_publication__gt=now,
                           sites=Site.objects.get_current(),
                           ) 


class EntryPublishedManager(models.Manager):
    """Manager to retrieve published entries"""

    def get_query_set(self):
        return entries_published(
            super(EntryPublishedManager, self).get_query_set(),
            )

    def search(self, pattern, blog_slug=''):
        lookup = models.Q()
        for pattern in pattern.split():
            q = models.Q(content__icontains=pattern) | \
                models.Q(excerpt__icontains=pattern) | \
                models.Q(title__icontains=pattern)
            lookup |= q
        filter = {}
        if ZINNIA_BLOG_ACTIVE:
             filter.update({'blog__slug': blog_slug})
        return self.get_query_set().filter(lookup, **filter)
