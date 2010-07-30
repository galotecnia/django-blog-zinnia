"""Views for zinnia entries search"""
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list
from django.shortcuts import get_object_or_404

from zinnia.models import Entry
from zinnia.models import Blog
from zinnia.settings import ZINNIA_BLOG_ACTIVE 



def entry_search(request, **kwargs):
    """Search entries matching with a pattern"""
    error = None
    pattern = None
    entries = Entry.published.none()
    
    blog_slug = ''
    blog = None
    if ZINNIA_BLOG_ACTIVE:
        blog_slug = kwargs.pop('blog_slug')
        blog = get_object_or_404(Blog, slug = blog_slug)
    if request.GET:
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            error = _('The pattern is too short')
        else:
            entries = Entry.published.search(pattern, blog_slug)
    else:
        error = _('No pattern to search found')
    extra_context={'error': error,
                   'pattern': pattern,
                  }
    if ZINNIA_BLOG_ACTIVE:
        extra_context.update({'blog': blog, 'filters':{'blog__slug': blog.slug}})

    return object_list(request, queryset=entries,
                       template_name='zinnia/entry_search.html',
                       extra_context=extra_context )

