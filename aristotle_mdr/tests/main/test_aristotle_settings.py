from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
import aristotle_mdr.tests.utils as utils

from django.core.exceptions import ImproperlyConfigured

from django.test.utils import setup_test_environment
setup_test_environment()

from aristotle_mdr.utils import fetch_aristotle_settings, error_messages


try:
    from unittest.mock import patch
except:
    # Python2, Py2
    from mock import patch

class TestAristotleSettings(TestCase):
    
    @patch('aristotle_mdr.utils.utils.logger')
    def test_bad_bulk_action_settings_log_correctly(self, mock_logger):
        with override_settings(
            ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, BULK_ACTIONS={}),
            ARISTOTLE_SETTINGS_STRICT_MODE=False
        ):
            my_settings = fetch_aristotle_settings()
            mock_logger.error.assert_called_with(error_messages['bulk_action_failed'])

        with override_settings(
            ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, BULK_ACTIONS={}),
            ARISTOTLE_SETTINGS_STRICT_MODE=True
        ):
            with self.assertRaises(ImproperlyConfigured):
                my_settings = fetch_aristotle_settings()


    @patch('aristotle_mdr.utils.utils.logger')
    def test_content_extensions_settings_log_correctly(self, mock_logger):
        with override_settings(
            ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, CONTENT_EXTENSIONS=[1]),
            ARISTOTLE_SETTINGS_STRICT_MODE=False
        ):
            my_settings = fetch_aristotle_settings()
            mock_logger.error.assert_called_with(error_messages['content_extensions_failed'])

        with override_settings(
            ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, CONTENT_EXTENSIONS=[1]),
            ARISTOTLE_SETTINGS_STRICT_MODE=True
        ):
            with self.assertRaises(ImproperlyConfigured):
                my_settings = fetch_aristotle_settings()

    @patch('aristotle_mdr.utils.utils.logger')
    def test_downloader_settings_log_correctly(self, mock_logger):
        with override_settings(
            ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, DOWNLOADERS=[1]),
            ARISTOTLE_SETTINGS_STRICT_MODE=False
        ):
            my_settings = fetch_aristotle_settings()
            mock_logger.error.assert_called_with(error_messages['downloaders_failed'])

        with override_settings(
            ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, DOWNLOADERS=[1]),
            ARISTOTLE_SETTINGS_STRICT_MODE=True
        ):
            with self.assertRaises(ImproperlyConfigured):
                my_settings = fetch_aristotle_settings()

    @patch('aristotle_mdr.utils.utils.logger')
    def test_management_command_logs_correctly(self, mock_logger):
        from django.core.management import call_command

        call_command('validate_aristotle_settings')

        with override_settings(
            ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, DOWNLOADERS=[1]),
            ARISTOTLE_SETTINGS_STRICT_MODE=True
        ):
            with self.assertRaises(ImproperlyConfigured):
                call_command('validate_aristotle_settings')
