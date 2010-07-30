"""Template tags for Zinnia"""
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

from random import sample
from urllib import urlencode
from datetime import datetime

from django.template import Library
from django.template import Node
from django.contrib.comments.templatetags.comments import CommentFormNode
from django.template.loader import render_to_string

from django import template

from zinnia.settings import ZINNIA_BLOG_ACTIVE
from zinnia.models import Entry
from zinnia.models import Category
from zinnia.comparison import VectorBuilder
from zinnia.comparison import pearson_score
from tagging.models import Tag

register = Library()

vectors = VectorBuilder({'queryset': Entry.published.all(),
                        'fields': ['title', 'excerpt', 'content']})
cache_entries_related = {}

@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_categories(context, template='zinnia/tags/categories.html'):
    """Return the categories"""
    filter = {}
    blog_slug = ''
    if ZINNIA_BLOG_ACTIVE:
        blog_slug = context.get('blog').slug
        filter.update({'entry__blog__slug': blog_slug})
    categories = []
    for cat in Category.objects.filter(**filter).distinct():
        cat_dict = {'category': cat, 
                    'entry_count': len(cat.entries_published_set(blog_slug))}
        categories.append(cat_dict)
    return {'template': template,
            'categories': categories}

@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_recent_entries(context, number=5, template='zinnia/tags/recent_entries.html'):
    """Return the most recent entries"""
    filter = {}
    if ZINNIA_BLOG_ACTIVE:
        blog_slug = context.get('blog').slug
        filter.update({'blog__slug': blog_slug})
    return {'template': template,
            'entries': Entry.published.filter(**filter)[:number]}

@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_random_entries(context, number=5, template='zinnia/tags/random_entries.html'):
    """Return random entries"""
    filter = {}
    if ZINNIA_BLOG_ACTIVE:
        blog_slug = context.get('blog').slug
        filter.update({'blog__slug': blog_slug})
    entries = Entry.published.filter(**filter)
    if number > len(entries):
        number = len(entries)
    return {'template': template,
            'entries': sample(entries, number)}

@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_popular_entries(context, number=5, template='zinnia/tags/popular_entries.html'):
    """Return popular  entries"""
    filter = {}
    if ZINNIA_BLOG_ACTIVE:
        blog_slug = context.get('blog').slug
        filter.update({'blog__slug': blog_slug})
    entries_comment = [(e, e.comments.count()) for e in Entry.published.filter(**filter)]
    entries_comment = sorted(entries_comment, key=lambda x: (x[1], x[0]),
                             reverse=True)[:number]
    entries = [entry for entry, n_comments in entries_comment]
    return {'template': template,
            'entries': entries}

@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_similar_entries(context, number=5, template='zinnia/tags/similar_entries.html'):
    """Return similar entries"""
    global vectors
    global cache_entries_related

    def compute_related(object_id, dataset):
        object_vector = None
        for entry, e_vector in dataset.items():
            if entry.pk == object_id:
                object_vector = e_vector

        if not object_vector:
            return []

        entry_related = {}
        for entry, e_vector in dataset.items():
            if entry.pk != object_id:
                score = pearson_score(object_vector, e_vector)
                if score:
                    entry_related[entry] = score

        related = sorted(entry_related.items(), key=lambda(k,v):(v,k))
        return [i for i, s in related]

    object_id = context['object'].pk
    columns, dataset = vectors()
    key = '%s-%s' % (object_id, vectors.key)
    if not key in cache_entries_related.keys():
        cache_entries_related[key] = compute_related(object_id, dataset)

    entries = cache_entries_related[key][:number]
    return {'template': template,
            'entries': entries}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_archives_entries(context, template='zinnia/tags/archives_entries.html'):
    """Return archives entries"""
    filter = {}
    out = {'template': template, 'ZINNIA_BLOG_ACTIVE': ZINNIA_BLOG_ACTIVE}
    if ZINNIA_BLOG_ACTIVE:
        blog = context.get('blog')
        filter.update({'blog__slug': blog.slug})
        out.update({'blog': blog})
    out.update({'archives': Entry.published.dates('creation_date', 'month',
                                order='DESC').filter(**filter)})
    print out
    return out

@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_calendar_entries(context, year=None, month=None,
                         template='zinnia/tags/calendar.html'):
    """Return an HTML calendar of entries"""
    if not year or not month:
        date_month = context.get('month') or context.get('day') or datetime.today()
        year, month = date_month.timetuple()[:2]
    
    blog = context.get('blog')
    try:
        from zinnia.templatetags.zcalendar import ZinniaCalendar
    except ImportError:
        return {'calendar': '<p class="notice">Calendar is unavailable for Python<2.5.</p>'}

    calendar = ZinniaCalendar()
    current_month = datetime(year, month, 1)
   
    filter = {}
    blog_slug = None
    if blog:
        blog_slug = blog.slug
        filter = {'blog__slug': blog_slug}
    dates = list(Entry.published.dates('creation_date', 
        'month').filter(**filter).distinct())

    next_month = previous_month = None
    if current_month in dates:
        index = dates.index(current_month)
        if index > 0:
            previous_month = dates[index - 1] 
        if index < len(dates) - 1:
            next_month = dates[index + 1]
    elif len(dates):
        for date in dates:
            if date < current_month:
                previous_month = date
            elif current_month < date:
                next_month = date
                break

    return {'template': template,
            'next_month': next_month,
            'previous_month': previous_month,
            'calendar': calendar.formatmonth(year, month, blog_slug = blog_slug)}

@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def zinnia_breadcrumbs(context, separator='/', root_name='Blog',
                       template='zinnia/tags/breadcrumbs.html',):                       
    """Return a breadcrumb for the application"""
    from zinnia.templatetags.zbreadcrumbs import retrieve_breadcrumbs
    
    blog_slug = None
    path = context['request'].path
    page_object = context.get('object') or context.get('category') or \
        context.get('tag') or context.get('author') or context.get('blog')
    if ZINNIA_BLOG_ACTIVE:
        blog_slug = context.get('blog').slug
    breadcrumbs = retrieve_breadcrumbs(path, page_object, root_name, blog_slug)

    return {'template': template,
            'separator': separator,
            'breadcrumbs': breadcrumbs}

@register.simple_tag
def get_gravatar(email, size, rating, default=None):
    """Return url for a Gravatar"""
    url = 'http://www.gravatar.com/avatar/%s.jpg' % md5(email).hexdigest()
    options = {'s': size, 'r': rating}
    if default:
        options['d'] = default

    url = '%s?%s' % (url, urlencode(options))
    return url.replace('&', '&amp;')

class EntryTagCloudNode(Node):
    """Tag related to an entry"""

    def __init__(self, filters):
        self.filters = template.Variable(filters)

    def render(self, context):
        try:
            filters = self.filters.resolve(context)
        except template.variabledoesnotexist:
            context['entries_tag_cloud'] = []
            return ''
        context['tag_cloud'] = Tag.objects.cloud_for_model(Entry, steps=6, filters = filters)
        return ''

def entry_tag_cloud(parser, token):
    try:
        templatetag_name, filters = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]
    return EntryTagCloudNode(filters)

register.tag(entry_tag_cloud)

class RenderCommentFormNode(CommentFormNode):
    """Return a comment form using blog owner dependences"""

    def __init__(self, object_expr, blog=''):
        self.object_expr = template.Variable(object_expr)
        self.blog = template.Variable(blog)

    def render(self, context):
        try:
            object_expr = self.object_expr.resolve(context)
            blog = self.blog.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "comments/form.html"
            ]
            context.push()
            formstr = render_to_string(template_search_list, {"form" : self.get_form(context)}, context)
            context.pop()
            return formstr
        else:
            return ''

# render's func block
def render_comment_blog_form(parser, token):
    try:
        templatetag_name, object_expr, blog = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]
    return RenderCommentFormNode(object_expr, blog)

register.tag(render_comment_blog_form)
