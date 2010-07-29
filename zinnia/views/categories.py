"""Views for zinnia categories"""
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from zinnia.models import Category
from zinnia.models import Blog
from zinnia.settings import PAGINATION
from zinnia.settings import ZINNIA_BLOG_ACTIVE


def category_detail(request, slug, page=None, **kwargs):
    """Display the entries of a category"""
    category = get_object_or_404(Category, slug=slug)
    extra_context = {'category': category}
    blog_slug = ''
    if ZINNIA_BLOG_ACTIVE:
        blog_slug = kwargs.pop('blog_slug')
        blog = get_object_or_404(Blog, slug = blog_slug)
        extra_context.update({'blog': blog})
    queryset = category.entries_published_set(blog_slug).distinct()
    return object_list(request, queryset, paginate_by=PAGINATION,page=page, extra_context=extra_context)

def category_list(request, page=None, **kwargs):
    """Display the general category list or blog's category list"""
    queryset = Category.objects.all()
    extra_context = {}
    if ZINNIA_BLOG_ACTIVE:
        blog_slug = kwargs.pop('blog_slug')
        blog = get_object_or_404(Blog, slug = blog_slug)
        extra_context = {'blog': blog}
        queryset = Category.objects.filter(entry__blog__slug = blog_slug).distinct()
    return object_list(request, queryset, paginate_by=PAGINATION,
                       page=page, extra_context=extra_context, **kwargs)
                
