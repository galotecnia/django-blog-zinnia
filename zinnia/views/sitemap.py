"""Views for zinnia sitemap"""
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.models import Blog
from zinnia.settings import ZINNIA_BLOG_ACTIVE 

def sitemap(*ka, **kw):
    """Wrapper around the direct to template generic view to
    force the update of the extra context"""
    entry_filter = {}
    category_filter = {}
    extra_context = {}
    if ZINNIA_BLOG_ACTIVE:
        blog_slug = kw.pop('blog_slug')
        blog = get_object_or_404(Blog, slug=blog_slug)
        entry_filter = {'blog__slug': blog_slug}
        category_filter = {'entry__blog__slug': blog_slug}            
        extra_context.update({'blog': blog})
    entries = Entry.published.filter(**entry_filter)
    categories = Category.objects.filter(**category_filter).distinct()
    extra_context.update({'entries': entries, 'categories': categories})    
    kw['extra_context'] = extra_context
    return direct_to_template(*ka, **kw)
