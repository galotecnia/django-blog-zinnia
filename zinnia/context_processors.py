"""Context Processors for zinnia"""
from zinnia import __version__
from zinnia.settings import MEDIA_URL
from zinnia.settings import ZINNIA_BLOG_ACTIVE

def media(request):
    """Adds media-related context variables to the context"""
    return {'ZINNIA_MEDIA_URL': MEDIA_URL}

def version(request):
    """Adds version of Zinnia to the context"""
    return {'ZINNIA_VERSION': __version__}

def blog_active(request):
    """Adds multi-blogs funcionality"""
    return {'ZINNIA_BLOG_ACTIVE': ZINNIA_BLOG_ACTIVE}

def blog_slug(request):
    """
        Add a blog_owner context variable and filter dict if it is found in request.session
        Needed in comment post and previw methods
    """
    out = {}
    if 'blog' in request.session.keys():
        out['blog'] = request.session.pop('blog')
        out['filter'] = {'blog__slug': out['blog'].slug}
    return out
