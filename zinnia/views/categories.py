"""Views for zinnia categories"""
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from zinnia.models import Category
from zinnia.settings import PAGINATION

def category_detail(request, blog_owner, slug, page=None):
    """Display the entries of a category"""
    category = get_object_or_404(Category, slug=slug)
    blog = get_object_or_404(Blog, blog_name = blog_owner)
    extra_context = {'category': category,
                     'blog_owner': blog_owner, 
                     'filter': {'blog__blog_name': blog_owner}, 
                     'read_more': True}
    return object_list(request, queryset=category.entries_published_set(blog_owner),
                       paginate_by=PAGINATION, page=page,
                       extra_context=extra_context)
