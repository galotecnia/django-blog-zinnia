"""Views for zinnia entries search"""
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from zinnia.models import Entry


def entry_search(request, blog_owner):
    """Search entries matching with a pattern"""
    error = None
    pattern = None
    entries = Entry.published.none()

    if request.GET:
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            error = _('The pattern is too short')
        else:
            entries = Entry.published.search(pattern, blog_owner)
    else:
        error = _('No pattern to search found')

    return object_list(request, queryset=entries,
                        template_name='zinnia/entry_search.html',
                        extra_context={'error': error,
                                       'pattern': pattern,
                                       'blog_owner': blog_owner,
                                       'filter': {'blog__blog_name': blog_owner}})

