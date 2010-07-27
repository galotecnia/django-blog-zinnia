"""Breadcrumb module for Zinnia templatetags"""
import re
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from zinnia.models import Blog

class Crumb(object):
    """Part of the Breadcrumbs"""
    def __init__(self, name, url=None):
        self.name = name
        self.url = url

def year_crumb(datetime, blog_slug = None):
    year = datetime.strftime('%Y')
    if blog_slug:
        return Crumb(year, reverse('zinnia_entry_archive_year', 
                    args=[blog_slug, year]))
    return Crumb(year, reverse('zinnia_entry_archive_year',args=[year]))

def month_crumb(datetime, blog_slug = None):
    year = datetime.strftime('%Y')
    month = datetime.strftime('%m')
    month_text = datetime.strftime('%b').capitalize()
    if blog_slug:
        return Crumb(month_text, reverse('zinnia_entry_archive_month', 
                    args=[blog_slug, year, month]))
    return Crumb(month_text, reverse('zinnia_entry_archive_month',
                args=[year, month]))

def day_crumb(datetime, blog_slug):
    year = datetime.strftime('%Y')
    month = datetime.strftime('%m')
    day = datetime.strftime('%d')
    if blog_slug:
        return Crumb(day, reverse('zinnia_entry_archive_day', 
                    args=[blog_slug, year, month, day]))
    return Crumb(day, reverse('zinnia_entry_archive_day',
                              args=[year, month, day]))

zinnia_root_url = lambda slug: reverse('zinnia_entry_archive_index', args=[slug]) if slug else reverse('zinnia_entry_archive_index')

archives_crumb = Crumb(_('Archives'))
tags_crumb = lambda slug: Crumb(_('Tags'), reverse('zinnia_tag_list', args=[slug]) if slug else reverse('zinnia_tag_list'))
authors_crumb = lambda slug: Crumb(_('Authors'), reverse('zinnia_author_list', args=[slug]) if slug else reverse('zinnia_author_list'))
categories_crumb = lambda slug: Crumb(_('Categories'), reverse('zinnia_category_list', args=[slug]) if slug else reverse('zinnia_category_list'))

MODEL_BREADCRUMBS = {'Tag': lambda x, slug: [tags_crumb(slug), Crumb(x.name)],
                     'User': lambda x, slug: [authors_crumb(slug), Crumb(x.username)],    
                     'Category': lambda x, slug: [categories_crumb(slug), Crumb(x.title)],
                     'Entry': lambda x, slug: [year_crumb(x.creation_date, slug),
                                         month_crumb(x.creation_date, slug),
                                         day_crumb(x.creation_date, slug),
                                         Crumb(x.title)],}

DATE_REGEXP = re.compile(r'.*(?P<year>\d{4})/(?P<month>\d{2})?/(?P<day>\d{2})?.*')


def retrieve_breadcrumbs(path, model_instance, root_name='', blog_slug = None):
    """Build a semi-hardcoded breadcrumbs
    based of the model's url handled by Zinnia"""
    breadcrumbs = []
   
    if blog_slug:
        root_name = get_object_or_404(Blog, slug = blog_slug).blog_name
        breadcrumbs.append(Crumb(_('Home'), reverse('blogs'))) 

    if root_name:
        breadcrumbs.append(Crumb(root_name, zinnia_root_url(blog_slug)))

    if model_instance is not None:
        key = model_instance.__class__.__name__
        if key in MODEL_BREADCRUMBS:
            breadcrumbs.extend(MODEL_BREADCRUMBS[key](model_instance, blog_slug))
            return breadcrumbs

    date_match = DATE_REGEXP.match(path)
    if date_match:
        date_dict = date_match.groupdict()
        path_date = datetime(
            int(date_dict['year']),
            date_dict.get('month') is not None and int(date_dict.get('month')) or 1,
            date_dict.get('day') is not None and int(date_dict.get('day')) or 1)
        
        date_breadcrumbs = [year_crumb(path_date, blog_slug)]
        if date_dict['month']: date_breadcrumbs.append(month_crumb(path_date, blog_slug))
        if date_dict['day']: date_breadcrumbs.append(day_crumb(path_date, blog_slug))
        breadcrumbs.extend(date_breadcrumbs)
        
        return breadcrumbs

    url_components = [comp for comp in
                      path.replace(zinnia_root_url(blog_slug), '').split('/') if comp]
    if len(url_components):
        breadcrumbs.append(Crumb(_(url_components[-1].capitalize())))

    return breadcrumbs
    
