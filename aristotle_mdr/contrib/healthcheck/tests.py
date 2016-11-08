import mock
from django.db import DatabaseError
from django.test import Client
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.unittest import TestCase
from django.test.utils import setup_test_environment

setup_test_environment()

cursor_wrapper = mock.Mock()
cursor_wrapper.side_effect = DatabaseError

class TestChaosMonkey(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_its_all_ok(self):
        # Test with no value
        response = self.client.get(reverse('aristotle_mdr_hb:health'))
        self.assertEqual(response.status_code, 200)

    # @mock.patch('django.db.backends.util.CursorWrapper', cursor_wrapper)
    # def test_dead_database(self):
    #     response = self.client.get(reverse('aristotle_mdr_hb:health'))
    #     print response.content
    #     self.assertEqual(response.status_code, 500)
