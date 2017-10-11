from django.test import TestCase

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
import aristotle_mdr.tests.utils as utils
from django.test.utils import override_settings
from django.core.management import call_command
from django.utils.six import StringIO


class CheckChecks(TestCase):

    def test_downloads_deprecated(self):
        def run_check():
            out = StringIO()
            call_command('check',
                interactive=False,
                verbosity=2,
                stdout=out,
                stderr=out,
            )
            return out.getvalue()

        self.assertFalse("aristotle_mdr.W001" in run_check())

        with override_settings(ARISTOTLE_DOWNLOADS=[]):
            self.assertTrue("aristotle_mdr.W001" in run_check())