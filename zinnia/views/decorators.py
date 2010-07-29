"""Decorators for zinnia.views"""

from zinnia.settings import ZINNIA_BLOG_ACTIVE
from zinnia.models import Blog
from django.shortcuts import get_object_or_404

def update_queryset(view, queryset, queryset_parameter='queryset'):
    """decorator around views based on a queryset
    passed in parameter, who will force the update
    of the queryset before executing the view.
    related to issue http://code.djangoproject.com/ticket/8378"""
    def wrap(*args, **kwargs):
        """regenerate the queryset before passing it to the view."""
        filter = {}
        if 'blog_slug' in kwargs:
            blog_slug = kwargs.pop('blog_slug')
            if ZINNIA_BLOG_ACTIVE and blog_slug:
                filter.update({'blog__slug': blog_slug})
                blog = get_object_or_404(Blog, slug = blog_slug)
                # blog_slug added as a context variable
                kwargs['extra_context'] = {'blog_slug': blog_slug, 'blog': blog}
        kwargs[queryset_parameter] = queryset().filter(**filter)
        return view(*args, **kwargs)
    return wrap
