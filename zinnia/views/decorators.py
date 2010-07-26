"""Decorators for zinnia.views"""

def update_queryset(view, queryset,
                    queryset_parameter='queryset'):
    """decorator around views based on a queryset
    passed in parameter, who will force the update
    of the queryset before executing the view.
    related to issue http://code.djangoproject.com/ticket/8378"""

    def wrap(*args, **kwargs):
        """regenerate the queryset before passing it to the view."""
        print "KWARGS", kwargs
        filter = {}
        if 'blog_slug' in kwargs:
            blog_slug = kwargs.pop('blog_slug')
            filter.update({'blog__blog_name': blog_slug})
        kwargs[queryset_parameter] = queryset().filter(**filter)
        print "ENTRY QUERYSET", kwargs[queryset_parameter]
        return view(*args, **kwargs)

    return wrap
