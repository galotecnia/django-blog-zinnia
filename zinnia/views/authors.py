"""Views for zinnia authors"""
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.generic.list_detail import object_list

from zinnia.managers import authors_published
from zinnia.managers import entries_published
from zinnia.views.decorators import update_queryset
from zinnia.settings import PAGINATION
from zinnia.settings import ZINNIA_BLOG_ACTIVE
from zinnia.models import Blog


author_list = update_queryset(object_list, authors_published)

def author_detail(request, **kwargs):
    """Display the entries of an author"""
    username = kwargs.pop('username')
    page = kwargs['page'] if 'page' in kwargs else None
    author = get_object_or_404(User, username=username)
    extra_context = {'author': author}
    filter = {}
    if ZINNIA_BLOG_ACTIVE:
        blog_slug = kwargs.pop('blog_slug')
        blog = get_object_or_404(Blog, slug = blog_slug)
        # We check if author is a blog author
        if author not in blog.authors.all():
            raise Http404('User not valid')
        extra_context.update({'blog_slug': blog_slug, 'blog': blog})
        filter = {'blog__slug': blog_slug}
    queryset = entries_published(author.entry_set).filter(**filter)
    return object_list(request, queryset=queryset, paginate_by=PAGINATION, 
                        page=page, extra_context=extra_context)
