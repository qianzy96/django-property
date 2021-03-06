import pytz
from urlparse import urlparse, parse_qsl
from urllib import urlencode
from datetime import datetime, timedelta

from django.test import TestCase,  RequestFactory
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.models import AnonymousUser

from homes.forms import SearchForm
from homes_for_sale.views import SearchPageView, UpdateDistanceView, DetailPageView
from homes_for_sale.querysets import SaleQuerySet
from homes_for_sale.forms import SaleDistanceForm, SaleContactForm
from homes.factories.alert_factory import AlertFactory
from homes.factories.user_factory import UserFactory
from homes_for_sale.factories.sale_factory import SaleFactory
from homes_for_sale.factories.sale_favourite_factory import SaleFavouriteFactory
from homes_for_sale.models import Sale

class BaseTestCase(TestCase):
    """Base test case with common functions"""
    def setUp(self):
        """
        Create a request factory
        """
        self.factory = RequestFactory()

    def initialize(self, view, request, *args, **kwargs):
        """
        Sets up view for testing
        """
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

    def parse_url(self, response):
        url = urlparse(response.url)
        query = dict(parse_qsl(url.query))
        return url, query


class SearchPageViewTestCase(BaseTestCase):
    """Tests the sales search page"""
    def test_template_name(self):
        """
        Test that the template name of the view is as expected
        """
        request = self.factory.get(reverse('sales:search') + '?latitude=0&longitude=1')

        request.user = AnonymousUser()

        response = SearchPageView.as_view()(request)

        # Check that the homes-for-sale-search.html template is used for this response
        self.assertIn('homes-for-sale/search.html',response.template_name)

    def test_get_queryset_long_lat_provided(self):
        """
        Test to check returns a SaleQuerySet when latitude and longitude provided
        """
        request = self.factory.get(reverse('sales:search') + '?latitude=0&longitude=1')

        request.user = AnonymousUser()

        view = super(SearchPageViewTestCase, self).initialize(SearchPageView(), request)

        # Check that the get_queryset function returns a SaleQuerySet
        self.assertIsInstance(view.get_queryset(), SaleQuerySet)

    def test_get_queryset_long_lat_missing(self):
        """
        Test to check throws 404 if long,lat missing
        """
        request = self.factory.get(reverse('sales:search'))

        request.user = AnonymousUser()

        view = super(SearchPageViewTestCase, self).initialize(SearchPageView(), request)

        # Check if the view.get_queryset() raises a 404 - it should as get_point tries to form
        # a GEOSGeometry with insufficient data, catches initial exception, rethrows new 404
        with self.assertRaises(Http404):
            view.get_queryset()

    def test_get_context_contains_keys(self):
        """
        Test that the context contains required keys in context
        """
        request = self.factory.get(reverse('sales:search'))
        request.user = AnonymousUser()

        view = super(SearchPageViewTestCase, self).initialize(SearchPageView(), request)
        view.object_list = []

        response = view.get_context_data()

        # Check contains distance, subscribed, paginator, view and form
        self.assertIn('distance', response)
        self.assertIn('subscribed', response)
        self.assertIn('paginator', response)
        self.assertIn('view', response)
        self.assertIn('form', response)

    def test_get_context_keys_correct_type(self):
        """
        Test that the context contains required keys in context
        """
        request = self.factory.get(reverse('sales:search'))
        request.user = AnonymousUser()

        view = super(SearchPageViewTestCase, self).initialize(SearchPageView(), request)
        view.object_list = []

        response = view.get_context_data()

        # Check contains distance as LettingDistanceForm and form as SearchForm
        self.assertIsInstance(response['distance'], SaleDistanceForm)
        self.assertIsInstance(response['form'], SearchForm)

    def test_get_context_unauthenticated_not_subscribed(self):
        """
        Test that on hitting the get_context function when anonymous returns
        false for subscribed value
        """
        request = self.factory.get(reverse('sales:search'))
        request.user = AnonymousUser()

        view = super(SearchPageViewTestCase, self).initialize(SearchPageView(), request)
        view.object_list = []

        response = view.get_context_data()

        # Check that the subscribed key is in context data and that subscribed is false
        # as the user is not authenticated and not subscribed
        self.assertIn('subscribed', response)
        self.assertFalse(response['subscribed'])

    def test_get_context_authenticated_not_subscribed(self):
        """
        Test that on hitting the get_context function when authenticated and subscribed to alert
        that subscribed returns true
        """
        user = UserFactory()

        request = self.factory.get(reverse('sales:search') + '?' + urlencode({'test1': 'test','test2': 'test'}))
        request.user = user

        view = super(SearchPageViewTestCase, self).initialize(SearchPageView(), request)
        view.object_list = []

        response = view.get_context_data()

        # Check that the context has the subscribed key and it is set to false as the user is logged in but there
        # are no alerts he/she is subscribed to
        self.assertIn('subscribed', response)
        self.assertFalse(response['subscribed'])

    def test_get_context_authenticated_and_subscribed(self):
        """
        Test that on hitting the get_context function when authenticated and subscribed to alert
        that subscribed returns true
        """
        user = UserFactory()

        # Subscribe the user to an alert
        alert = AlertFactory(user=user, criteria={'test1': 'test','test2': 'test'})

        request = self.factory.get(reverse('sales:search') + '?' + urlencode({'test1': 'test','test2': 'test'}))
        request.user = user

        view = super(SearchPageViewTestCase, self).initialize(SearchPageView(), request)
        view.object_list = []

        response = view.get_context_data()

        # Check if the context has the subscribed key and that it is set to true
        self.assertIn('subscribed', response)
        self.assertTrue(response['subscribed'])


class DetailPageViewTestCase(BaseTestCase):
    """Tests the detail page for sales"""

    def test_template_name(self):
        """
        Test that the template name of the view is as expected
        """
        sale = SaleFactory()
        request = self.factory.get(reverse('sales:detail', kwargs={
            'slug': sale.slug
        }))

        request.user = UserFactory()

        response = DetailPageView.as_view()(request, slug=sale.slug)

        # Check that the correct template is used for the view
        self.assertIn('homes-for-sale/detail.html', response.template_name)

    def test_get_context_contains_keys(self):
        """
        Test that the context contains required keys in context
        """
        sale = SaleFactory()
        request = self.factory.get(reverse('sales:detail', kwargs={
            'slug': sale.slug
        }))

        request.user = UserFactory()

        response = DetailPageView.as_view()(request, slug=sale.slug)

        # Check that the context contains the correct keys
        self.assertIn('contact', response.context_data)
        self.assertIn('favourited', response.context_data)
        self.assertIn('form', response.context_data)
        self.assertIn('google', response.context_data)
        self.assertIn('recaptcha', response.context_data)

    def test_get_context_keys_correct_type(self):
        """
        Test that the context contains required keys in context
        """
        sale = SaleFactory()

        request = self.factory.get(reverse('sales:detail', kwargs={
            'slug': sale.slug
        }))

        request.user = UserFactory()

        response = DetailPageView.as_view()(request, slug=sale.slug)

        # Check contains contact as SaleContactForm and form as SearchForm
        self.assertIsInstance(response.context_data['contact'], SaleContactForm)
        self.assertIsInstance(response.context_data['form'], SearchForm)

    def test_favourited_context_is_true(self):
        """
        Test that a property is favourited by the user
        """
        favourite = SaleFavouriteFactory()

        request = self.factory.get(reverse('sales:detail', kwargs={
            'slug': favourite.property.slug
        }))

        request.user = favourite.user

        response = DetailPageView.as_view()(request, slug=favourite.property.slug)

        # Check that the favourited context data is found but that it is set to true it is favourited
        self.assertIn('favourited', response.context_data)
        self.assertTrue(response.context_data['favourited'])

    def test_favourited_context_is_false(self):
        """
         Test that a property is favourited by the user
         """
        favourite = SaleFavouriteFactory()

        request = self.factory.get(reverse('sales:detail', kwargs={
            'slug': favourite.property.slug
        }))

        request.user = UserFactory()

        response = DetailPageView.as_view()(request, slug=favourite.property.slug)

        # Check that the favourited context data is found but that it is set to false (not favourited)
        self.assertIn('favourited', response.context_data)
        self.assertFalse(response.context_data['favourited'])

    def test_favourited_context_user_anon(self):
        """
         Test that a property is not favourited by a anonymous user
         """
        favourite = SaleFavouriteFactory()

        request = self.factory.get(reverse('sales:detail', kwargs={
            'slug': favourite.property.slug
        }))

        request.user = AnonymousUser()

        response = DetailPageView.as_view()(request, slug=favourite.property.slug)

        # Check that the favourited context data is found but that it is set to false (not favourited)
        self.assertIn('favourited', response.context_data)
        self.assertFalse(response.context_data['favourited'])

    def test_get_queryset(self):
        """
         Test that the queryset returned is as expected a SaleQuerySet
         """
        sale = SaleFactory()

        request = self.factory.get(reverse('sales:detail', kwargs={
            'slug': sale.slug
        }))

        view = super(DetailPageViewTestCase, self).initialize(DetailPageView(), request, kwargs={'slug':sale.slug})

        response = view.get_queryset()

        # Check if response is LettingQuerySet
        self.assertIsInstance(response, SaleQuerySet)

    def test_get_queryset_not_published(self):
        """
         Test that the queryset returned is as expected a LettingQuerySet
         """
        sale = SaleFactory.create(status=Sale.STATUS_CHOICE_INACTIVE)

        request = self.factory.get(reverse('sales:detail', kwargs={
            'slug': sale.slug
        }))

        request.user = AnonymousUser()

        with self.assertRaises(Http404):
            DetailPageView.as_view()(request, slug=sale.slug)

    def test_get_queryset_expired(self):
        """
         Test that the queryset returned is as expected a LettingQuerySet
         """
        expired_date = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=1)
        sale = SaleFactory.create(expires_at=expired_date)

        request = self.factory.get(reverse('sales:detail', kwargs={
            'slug': sale.slug
        }))

        request.user = AnonymousUser()

        with self.assertRaises(Http404):
            DetailPageView.as_view()(request, slug=sale.slug)


class UpdateDistanceViewTestCase(BaseTestCase):
    """Tests the update distance post function"""

    def test_post_update_distance_success(self):
        """
        Check that posting an updated distance to url returns a /sales/search/ path with the updated distance
        """
        request = self.factory.post(reverse('sales:distance'), {'distance':10}, HTTP_REFERER='/sales/search/?distance=5')

        view = super(UpdateDistanceViewTestCase, self).initialize(UpdateDistanceView(), request)

        response = view.post(request)

        (url, query) = super(UpdateDistanceViewTestCase, self).parse_url(response)

        # Check that an HTTPResponseRedirect occurred, that the path was /sales/search/ and that the querystring for
        # the redirect contains the key distance and has the value 10
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(url.path, '/sales/search/')
        self.assertIn('distance', query)
        self.assertEqual(query['distance'],'10')

    def test_post_update_distance_failure(self):
        """
        Check that posting an unacceptable value causes a 404 as form validation fails
        """
        request = self.factory.post(reverse('sales:distance'), {'distance':'x'}, HTTP_REFERER='/sales/search/?distance=5')

        view = super(UpdateDistanceViewTestCase, self).initialize(UpdateDistanceView(), request)

        # Check that a 404 is thrown as the distance value sent in post is invalid
        with self.assertRaises(Http404):
            view.post(request)

