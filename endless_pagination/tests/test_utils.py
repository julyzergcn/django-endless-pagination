"""Utilities tests."""

from __future__ import unicode_literals

from django.test import TestCase
from django.test.client import RequestFactory

from endless_pagination import utils
from endless_pagination.settings import PAGE_LABEL
from endless_pagination.exceptions import PaginationError


class GetDataFromContextTest(TestCase):

    def test_valid_context(self):
        # Ensure the endless data is correctly retrieved from context.
        context = {'endless': 'test-data'}
        self.assertEqual('test-data', utils.get_data_from_context(context))

    def test_invalid_context(self):
        # A ``PaginationError`` is raised if the data cannot be found
        # in the context.
        self.assertRaises(PaginationError, utils.get_data_from_context, {})


class GetPageNumberFromRequestTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_no_querystring_key(self):
        # Ensure the first page is returned if page info cannot be
        # retrieved from the querystring.
        request = self.factory.get('/')
        self.assertEqual(1, utils.get_page_number_from_request(request))

    def test_default_querystring_key(self):
        # Ensure the default page label is used if ``querystring_key``
        # is not provided.
        request = self.factory.get('?{0}=2'.format(PAGE_LABEL))
        self.assertEqual(2, utils.get_page_number_from_request(request))

    def test_default(self):
        # Ensure the default page number is returned if page info cannot be
        # retrieved from the querystring.
        request = self.factory.get('/')
        page_number = utils.get_page_number_from_request(request, default=3)
        self.assertEqual(3, page_number)

    def test_custom_querystring_key(self):
        # Ensure the page returned correctly reflects the ``querystring_key``.
        request = self.factory.get('?mypage=4'.format(PAGE_LABEL))
        page_number = utils.get_page_number_from_request(
            request, querystring_key='mypage')
        self.assertEqual(4, page_number)

    def test_post_data(self):
        # The page number can also be present in POST data.
        request = self.factory.post('/', {PAGE_LABEL: 5})
        self.assertEqual(5, utils.get_page_number_from_request(request))


class GetPageNumbersTest(TestCase):

    def test_defaults(self):
        # Ensure the pages are returned correctly using the default values.
        pages = utils.get_page_numbers(10, 20)
        expected = [
            'previous', 1, 2, 3, None, 8, 9, 10, 11, 12,
            None, 18, 19, 20, 'next']
        self.assertSequenceEqual(expected, pages)

    def test_first_page(self):
        # Ensure the correct pages are returned if the first page is requested.
        pages = utils.get_page_numbers(1, 10)
        expected = [1, 2, 3, None, 8, 9, 10, 'next']
        self.assertSequenceEqual(expected, pages)

    def test_last_page(self):
        # Ensure the correct pages are returned if the last page is requested.
        pages = utils.get_page_numbers(10, 10)
        expected = ['previous', 1, 2, 3, None, 8, 9, 10]
        self.assertSequenceEqual(expected, pages)

    def test_no_extremes(self):
        # Ensure the correct pages are returned with no extremes.
        pages = utils.get_page_numbers(10, 20, extremes=0)
        expected = ['previous', 8, 9, 10, 11, 12, 'next']
        self.assertSequenceEqual(expected, pages)

    def test_no_arounds(self):
        # Ensure the correct pages are returned with no arounds.
        pages = utils.get_page_numbers(10, 20, arounds=0)
        expected = ['previous', 1, 2, 3, None, 10, None, 18, 19, 20, 'next']
        self.assertSequenceEqual(expected, pages)

    def test_no_extremes_arounds(self):
        # Ensure the correct pages are returned with no extremes and arounds.
        pages = utils.get_page_numbers(10, 20, extremes=0, arounds=0)
        expected = ['previous', 10, 'next']
        self.assertSequenceEqual(expected, pages)

    def test_one_page(self):
        # Ensure the correct pages are returned if there is only one page.
        pages = utils.get_page_numbers(1, 1)
        expected = [1]
        self.assertSequenceEqual(expected, pages)


class GetElasticPageNumbersTest(TestCase):

    def _run_tests(self, test_data):
        for current_page, num_pages, expected in test_data:
            pages = utils.get_elastic_page_numbers(current_page, num_pages)
            self.assertSequenceEqual(expected, pages)

    def test_units(self):
        test_data = (
            (1, 1, [1]),
            (1, 2, [1, 2]),
            (2, 2, [1, 2]),
            (1, 3, [1, 2, 3]),
            (3, 3, [1, 2, 3]),
            (1, 4, [1, 2, 3, 4]),
            (4, 4, [1, 2, 3, 4]),
            (1, 5, [1, 2, 3, 4, 5]),
            (5, 5, [1, 2, 3, 4, 5]),
            (1, 6, [1, 2, 3, 4, 5, 6]),
            (6, 6, [1, 2, 3, 4, 5, 6]),
            (1, 7, [1, 2, 3, 4, 5, 6, 7]),
            (7, 7, [1, 2, 3, 4, 5, 6, 7]),
            (1, 8, [1, 2, 3, 4, 5, 6, 7, 8]),
            (8, 8, [1, 2, 3, 4, 5, 6, 7, 8]),
            (1, 9, [1, 2, 3, 4, 5, 6, 7, 8, 9]),
            (9, 9, [1, 2, 3, 4, 5, 6, 7, 8, 9]),
            (1, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
            (6, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
            (10, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        )
        self._run_tests(test_data)

    def test_tens(self):
        test_data = (
            (1, 11, [1, 4, 8, 11, 'next', 'last']),
            (2, 11, ['first', 'previous', 1, 2, 5, 8, 11, 'next', 'last']),
            (3, 11, ['first', 'previous', 1, 3, 6, 8, 11, 'next', 'last']),
            (4, 11, ['first', 'previous', 1, 4, 7, 8, 11, 'next', 'last']),
            (5, 11, ['first', 'previous', 1, 5, 8, 11, 'next', 'last']),
            (6, 11, ['first', 'previous', 1, 6, 11, 'next', 'last']),
            (7, 11, ['first', 'previous', 1, 4, 7, 11, 'next', 'last']),
            (8, 11, ['first', 'previous', 1, 4, 5, 8, 11, 'next', 'last']),
            (9, 11, ['first', 'previous', 1, 4, 6, 9, 11, 'next', 'last']),
            (10, 11, ['first', 'previous', 1, 4, 7, 10, 11, 'next', 'last']),
            (11, 11, ['first', 'previous', 1, 4, 8, 11]),
        )
        self._run_tests(test_data)


class GetQuerystringForPageTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_querystring(self):
        # Ensure the querystring is correctly generated from request.
        request = self.factory.get('/')
        querystring = utils.get_querystring_for_page(request, 2, 'mypage')
        self.assertEqual('?mypage=2', querystring)

    def test_default_page(self):
        # Ensure the querystring is empty for the default page.
        request = self.factory.get('/')
        querystring = utils.get_querystring_for_page(
            request, 3, 'mypage', default_number=3)
        self.assertEqual('', querystring)

    def test_composition(self):
        # Ensure existing querystring is correctly preserved.
        request = self.factory.get('/?mypage=1&foo=bar')
        querystring = utils.get_querystring_for_page(request, 4, 'mypage')
        self.assertIn('mypage=4', querystring)
        self.assertIn('foo=bar', querystring)

    def test_querystring_key(self):
        # The querystring key is deleted from the querystring if present.
        request = self.factory.get('/?querystring_key=mykey')
        querystring = utils.get_querystring_for_page(request, 5, 'mypage')
        self.assertEqual('?mypage=5', querystring)
