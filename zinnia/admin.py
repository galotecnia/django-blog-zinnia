"""Admin of Zinnia"""
from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.utils.text import truncate_words
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse, NoReverseMatch

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.models import Blog
from zinnia.managers import PUBLISHED
from zinnia.settings import USE_BITLY
from zinnia.settings import USE_TWITTER
from zinnia.settings import TWITTER_USER
from zinnia.settings import TWITTER_PASSWORD
from zinnia.settings import PING_DIRECTORIES
from zinnia.settings import SAVE_PING_DIRECTORIES
from zinnia.settings import ZINNIA_BLOG_ACTIVE
from zinnia.ping import DirectoryPinger
from zinnia.managers import entries_published

class CategoryAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'description')
    list_display = ('title', 'slug', 'description')
    list_filter = ('title', 'slug')
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'description')

class BlogAdmin(admin.ModelAdmin):
    fields = ('authors', 'blog_name', 'slug')
    list_display = ('blog_name', )
    list_filter = ('blog_name', 'authors', 'slug')
    prepopulated_fields = {'slug': ('blog_name', )}
    search_fields = ('blog_name', 'authors')

class EntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    fieldsets = ((_('Content'), {'fields': ('title', 'content', 'image', 'status', 'blog')}),
                 (_('Options'), {'fields': ('slug', 'excerpt', 'related', 'author',
                                            'creation_date', 'start_publication',
                                            'end_publication', 'comment_enabled'),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Sorting'), {'fields': ('sites', 'categories', 'tags')}))
    list_filter = ('categories', 'status', 'comment_enabled',
                   'creation_date', 'start_publication', 'end_publication', 'blog')
    list_display = ('get_title', 'get_authors', 'get_categories',
                    'get_tags', 'get_sites', 'comment_enabled',
                    'get_is_actual', 'get_is_visible', 'get_link',
                    'get_short_url', 'creation_date', 'last_update')
    filter_horizontal = ('categories', 'related')
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'excerpt', 'content', 'tags')
    actions = ['make_mine', 'make_published', 'make_hidden', 'close_comments',
               'ping_directories', 'make_tweet']
    actions_on_top = True
    actions_on_bottom = True

    # Custom Display
    def get_title(self, entry):
        """Return the title with word count and number of comments"""
        title = _('%(title)s (%(word_count)i words)') % \
                {'title': entry.title, 'word_count': entry.word_count}
        comments = entry.comments.count()
        if comments:
            return _('%(title)s (%(comments)i comments)') % \
                   {'title': title, 'comments': comments}
        return title
    get_title.short_description = _('title')

    def get_authors(self, entry):
        """Return the authors in HTML"""
        try:
            author = '<a href="%s" target="blank">%s</a>' % \
                (reverse('zinnia_author_detail', args=[entry.author.username]),
                entry.author.username)
        except NoReverseMatch:
            author = entry.author.username 
        return author
    get_authors.allow_tags = True
    get_authors.short_description = _('author(s)')

    def get_categories(self, entry):
        """Return the categories linked in HTML"""
        try:
            categories = ['<a href="%s" target="blank">%s</a>' %
                          (category.get_absolute_url(), category.title)
                          for category in entry.categories.all()]
        except NoReverseMatch:
            categories = [category.title for category in entry.categories.all()]
        return ', '.join(categories)
    get_categories.allow_tags = True
    get_categories.short_description = _('category(s)')

    def get_tags(self, entry):
        """Return the tags linked in HTML"""
        try:
            return ', '.join(['<a href="%s" target="blank">%s</a>' %
                              (reverse('zinnia_tag_detail', args=[tag]), tag)
                              for tag in entry.tags.replace(',', '').split()])
        except NoReverseMatch:
            return ', '.join(entry.tags.replace(',', '').split())
    get_tags.allow_tags = True
    get_tags.short_description = _('tag(s)')

    def get_sites(self, entry):
        """Return the sites linked in HTML"""
        return ', '.join(['<a href="http://%(domain)s" target="blank">%(name)s</a>' %
                          site.__dict__ for site in entry.sites.all()])
    get_sites.allow_tags = True
    get_sites.short_description = _('site(s)')

    def get_is_actual(self, entry):
        """Admin wrapper for entry.is_actual"""
        return entry.is_actual
    get_is_actual.boolean = True
    get_is_actual.short_description = _('is actual')

    def get_is_visible(self, entry):
        """Admin wrapper for entry.is_visible"""
        return entry.is_visible
    get_is_visible.boolean = True
    get_is_visible.short_description = _('is visible')

    def get_link(self, entry):
        """Return a formated link to the entry"""
        return _('<a href="%s" target="blank">View</a>') % entry.get_absolute_url()
    get_link.allow_tags = True
    get_link.short_description = _('View on site')

    def get_short_url(self, entry):
        url = entry.short_url
        if not url:
            return _('Unavailable')
        return '<a href="%(url)s" target="blank">%(url)s</a>' % \
               {'url': url}
    get_short_url.allow_tags = True
    get_short_url.short_description = _('short url')

    # Custom Methods
    def save_model(self, request, entry, form, change):
        """Save the authors, update time, make an excerpt"""
        if not form.cleaned_data.get('excerpt'):
            entry.excerpt = truncate_words(strip_tags(entry.content), 50)

        if entry.pk and not request.user.has_perm('zinnia.can_change_author'):
            form.cleaned_data['author'] = entry.author

        if not form.cleaned_data.get('author'):
            entry.author = request.user

        entry.last_update = datetime.now()
        entry.save()

        if entry.is_visible and SAVE_PING_DIRECTORIES:
            self.ping_directories(request, [entry])

    def queryset(self, request):
        """Make special filtering by user permissions"""
        queryset = super(EntryAdmin, self).queryset(request)
        if request.user.has_perm('zinnia.can_view_all'):
            return queryset
        return Entry.objects.filter(author = request.user)


    def remove_field(self, field):
        """Remove from object admin form a given field"""
        for name, content in self.fieldsets:
            if content['fields'].__contains__(field):
                content['fields'] = [i for i in content['fields'] if i != field]

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Hide author field if you are not superadmin"""
        if db_field.name == 'author' and not kwargs['request'].user.is_superuser:
            self.remove_field('author')
            return
        return super(EntryAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter queryset by blog_owner, if needed"""
        if db_field.name == "blog":
            if ZINNIA_BLOG_ACTIVE and (request.user.is_superuser == False):
                kwargs["queryset"] = request.user.blog_set.all()
            elif not ZINNIA_BLOG_ACTIVE:
                self.remove_field('blog')
                return
        return super(EntryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Filters the disposable authors"""
        if ZINNIA_BLOG_ACTIVE:
            if db_field.name == 'authors':
                if request.user.has_perm('zinnia.can_change_author'):
                    kwargs['queryset'] = User.objects.filter(is_staff=True)
                else:
                    kwargs['queryset'] = User.objects.filter(pk=request.user.pk)
            # Filter queryset by blog_onwer
            if (request.user.is_superuser == False) and (db_field.name == "related"):
                kwargs["queryset"] = Entry.published.filter(blog__authors = request.user)
                return db_field.formfield(**kwargs)

        return super(EntryAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def get_actions(self, request):
        """Define user actions by permissions"""
        actions = super(EntryAdmin, self).get_actions(request)
        if not request.user.has_perm('zinnia.can_change_author') \
           or not request.user.has_perm('zinnia.can_view_all'):
            del actions['make_mine']
        if not PING_DIRECTORIES:
            del actions['ping_directories']
        if not USE_TWITTER or not USE_BITLY:
            del actions['make_tweet']

        return actions

    # Custom Actions
    def make_mine(self, request, queryset):
        """Set the entries to the user"""
        for entry in queryset:
            if request.user in entry.blog.authors.all():
                entry.author = request.user
                entry.save()
    make_mine.short_description = _('Set the entries to the user')

    def make_published(self, request, queryset):
        """Set entries selected as published"""
        queryset.update(status=PUBLISHED)
    make_published.short_description = _('Set entries selected as published')

    def make_hidden(self, request, queryset):
        """Set entries selected as hidden"""
        queryset.update(status='hidden')
    make_hidden.short_description = _('Set entries selected as hidden')

    def make_tweet(self, request, queryset):
        """Post an update on Twitter"""
        import twitter
        api = twitter.Api(username=TWITTER_USER, password=TWITTER_PASSWORD)
        for entry in queryset:
            message = '%s %s' % (entry.title[:119], entry.short_url)
            api.PostUpdate(message)
    make_tweet.short_description = _('Tweet entries selected')

    def close_comments(self, request, queryset):
        """Close the comments for selected entries"""
        queryset.update(comment_enabled=False)
    close_comments.short_description = _('Close the comments for selected entries')

    def ping_directories(self, request, queryset):
        """Ping Directories for selected entries"""
        success = 0
        for directory in PING_DIRECTORIES:
            pinger = DirectoryPinger(directory)
            for entry in queryset:
                response = pinger.ping(entry)
                if not response.get('flerror', True):
                    success += 1
        self.message_user(request, _('%i directories succesfully pinged.') % success)
    ping_directories.short_description = _('Ping Directories for selected entries')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Blog, BlogAdmin)
