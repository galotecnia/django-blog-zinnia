"""Calendar module for Zinnia templatetags"""
from datetime import date
from calendar import LocaleHTMLCalendar
from django.core.urlresolvers import reverse

from zinnia.models import Entry
from zinnia.models import Blog
from zinnia.settings import ZINNIA_BLOG_ACTIVE

day_reverse = lambda day_date, slug: reverse('zinnia_entry_archive_day', \
    args=[slug, day_date.strftime('%Y'), day_date.strftime('%m'), day_date.strftime('%d')]) \
    if slug else reverse('zinnia_entry_archive_day', \
    args=[day_date.strftime('%Y'), day_date.strftime('%m'), day_date.strftime('%d')])

class ZinniaCalendar(LocaleHTMLCalendar):
    """Override of LocaleHTMLCalendar"""

    def formatday(self, day, weekday):
        if day and day in self.day_entries:
            day_date = date(self.current_year, self.current_month, day)
            archive_day_url = day_reverse(day_date, self.blog_slug)
            return '<td class="%s entry"><a href="%s">%d</a></td>' % (
                self.cssclasses[weekday], archive_day_url, day)
        
        return super(ZinniaCalendar, self).formatday(day, weekday)

    def formatmonth(self, theyear, themonth, withyear=True, blog_slug = None):
        self.blog_slug = blog_slug
        self.current_year = theyear
        self.current_month = themonth
        filter = {'creation_date__year': theyear, 'creation_date__month': themonth}
        if blog_slug: 
            filter.update({'blog__slug': blog_slug})
        self.day_entries = [entries.creation_date.day for entries in
                            Entry.published.filter(**filter)]

        return super(ZinniaCalendar, self).formatmonth(theyear, themonth, withyear)


