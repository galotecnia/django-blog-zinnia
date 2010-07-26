"""Views for zinnia authors"""
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from zinnia.settings import PAGINATION
from zinnia.managers import authors_published
from zinnia.managers import entries_published
from zinnia.views.decorators import update_queryset


author_list = update_queryset(object_list, authors_published)

def author_detail(request, username, page=None):
    """Display the entries of an author"""
    author = get_object_or_404(User, username=username)
    blog = get_object_or_404(Blog, blog_name = blog_owner)
    return object_list(request, queryset=entries_published(author.entry_set),
                       paginate_by=PAGINATION, page=page,
                       extra_context={'author': author,
                                      'blog_owner': blog_owner,
                                      'filter': {'blog__authors__username': username}})
