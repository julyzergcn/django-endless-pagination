"""On scroll pagination integration tests."""

from endless_pagination.tests.integration import SeleniumTestCase


class OnScrollPaginationTest(SeleniumTestCase):

    view_name = 'onscroll'

    def test_new_elements_loaded(self):
        # Ensure a new page is loaded on scroll.
        self.get()
        with self.assertNewElements('object', range(1, 11)):
            self.scroll_down()

    def test_url_not_changed(self):
        # Ensure the request is done using Ajax (the page does not refresh).
        self.get()
        with self.assertSameURL():
            self.scroll_down()

    def test_direct_link(self):
        # Ensure direct links work.
        self.get(page=4)
        self.assertElements('object', range(16, 21))
        self.assertIn('page=4', self.selenium.current_url)

    def test_subsequent_page(self):
        # Ensure next page is correctly loaded in a subsequent page.
        self.get(page=2)
        with self.assertNewElements('object', range(6, 16)):
            self.scroll_down()

    def test_multiple_show_more(self):
        # Ensure new pages are loaded again and again.
        self.get()
        for page in range(2, 5):
            expected_range = range(1, 5 * page + 1)
            with self.assertSameURL():
                with self.assertNewElements('object', expected_range):
                    self.scroll_down()

    def test_scrolling_last_page(self):
        # Ensure scrolling on the last page is a no-op.
        self.get(page=10)
        with self.assertNewElements('object', range(46, 51)):
            self.scroll_down()
