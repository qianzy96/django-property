from django.utils.translation import ugettext as _
from django.urls import reverse
from django.contrib.sites.models import Site

from homes.models import *
from .querysets import LettingQuerySet


class Letting(Property):
    RENTAL_PERIOD_WEEKLY = 1
    RENTAL_PERIOD_MONTHLY = 2
    RENTAL_PERIOD_ANNUALLY = 3
    RENTAL_PERIOD_CHOICES = (
        (RENTAL_PERIOD_WEEKLY, _('Weekly')),
        (RENTAL_PERIOD_MONTHLY, _('Monthly')),
        (RENTAL_PERIOD_ANNUALLY, _('Annually'))
    )
    TYPE_OF_LET_LONG_TERM = 1
    TYPE_OF_LET_SHORT_TERM = 2
    TYPE_OF_LET_STUDENT = 3
    TYPE_OF_LET_CHOICES = (
        (TYPE_OF_LET_LONG_TERM, _('Long Term')),
        (TYPE_OF_LET_SHORT_TERM, _('Short Term')),
        (TYPE_OF_LET_STUDENT, _('Student'))
    )
    rental = models.DecimalField(max_digits=11, decimal_places=2)
    period = models.IntegerField(choices=RENTAL_PERIOD_CHOICES)
    type_of_let = models.IntegerField(choices=TYPE_OF_LET_CHOICES)
    furnished = models.BooleanField(default=False)
    house_share = models.BooleanField(default=False)
    let_agreed = models.BooleanField(default=False)
    available_at = models.DateTimeField()
    filtered = LettingQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('lettings:detail', kwargs={'slug':self.slug})

    def get_full_absolute_url(self):
        site = Site.objects.get_current()
        return '{}{}'.format(str(site.domain), self.get_absolute_url())

    class Meta:
        verbose_name = _('property')
        verbose_name_plural = _('properties')


class LettingFeature(Feature):
    property = models.ForeignKey(Letting)

    class Meta:
        verbose_name = _('feature')
        verbose_name_plural = _('features')


class LettingPicture(Picture):
    property = models.ForeignKey(Letting)

    class Meta:
        verbose_name = _('picture')
        verbose_name_plural = _('pictures')


class LettingMedia(Media):
    property = models.ForeignKey(Letting)

    class Meta:
        verbose_name = _('media item')
        verbose_name_plural = _('media items')


class LettingContact(Contact):
    property = models.ForeignKey(Letting)

    class Meta:
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')


class LettingNote(Note):
    property = models.ForeignKey(Letting)

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')


class LettingFavourite(Favourite):
    property = models.ForeignKey(Letting)

    class Meta:
        verbose_name = "favourite"
        verbose_name_plural = _('favourites')