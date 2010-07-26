"""Context Processors for zinnia"""
from zinnia import __version__
from zinnia.settings import MEDIA_URL

def media(request):
    """Adds media-related context variables to the context"""
    return {'ZINNIA_MEDIA_URL': MEDIA_URL}

def version(request):
    """Adds version of Zinnia to the context"""
    return {'ZINNIA_VERSION': __version__}

def blog_owner(request):
    """Add a blog_owner context variable and filter dict if it is found in request.session"""
    out = {}
    if 'blog_owner' in request.session.keys():
        out['blog_owner'] = request.session.pop('blog_owner')
        out['filter'] = {'blog__blog_name': out['blog_owner']}
    return out
