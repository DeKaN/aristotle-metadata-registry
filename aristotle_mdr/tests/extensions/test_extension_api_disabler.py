from django.test import TestCase

import aristotle_mdr.tests.utils as utils
from django.core.urlresolvers import reverse
from django.template import TemplateDoesNotExist
from aristotle_mdr.tests.main.test_html_pages import LoggedInViewConceptPages
from aristotle_mdr.tests.main.test_admin_pages import AdminPageForConcept
from django.test.utils import override_settings

from extension_test.models import Question, Questionnaire

from django.test.utils import setup_test_environment

from aristotle_mdr.required_settings import ARISTOTLE_SETTINGS as BASE_ARISTOTLE_SETTINGS
from aristotle_mdr.utils import fetch_metadata_apps
from django.core.management import call_command
from django.conf import settings


class ConfigDisableCheckTests(utils.LoggedInViewPages, TestCase):
    def setUp(self):
        super(ConfigDisableCheckTests, self).setUp()
        self.item = Question.objects.create(
            name="Test Question Title",
            definition="Some unique string"
        )

    def tearDown(self):
        call_command('clear_index', interactive=False, verbosity=0)

    def setup_help(self):
        call_command('load_aristotle_help')
        from aristotle_mdr.contrib.help.models import HelpPage
        self.assertTrue(
            HelpPage.objects.filter(
                app_label='extension_test',title="My very specific help page"
            ).exists()
        )

    def test_help_visible_if_enabled(self):
        self.setup_help()
        self.assertTrue('extension_test' in fetch_metadata_apps())

        response = self.client.get(reverse('aristotle_help:help_base'))
        self.assertContains(response, "My very specific help page")

        response = self.client.get(reverse('aristotle_help:help_concepts'))
        self.assertContains(response, "Question")

        response = self.client.get(reverse('aristotle_help:concept_app_help', args=['extension_test']))
        self.assertContains(response, "Question")

        response = self.client.get(reverse('aristotle_help:concept_help', args=['extension_test', 'question']))
        self.assertContains(response, "Question")

    @override_settings(ARISTOTLE_SETTINGS=dict(
        settings.ARISTOTLE_SETTINGS,
        CONTENT_EXTENSIONS=BASE_ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'] + ['aristotle_mdr_links']
    ))
    def test_help_not_visible_if_disabled(self):
        self.setup_help()
        self.assertFalse('extension_test' in fetch_metadata_apps())

        response = self.client.get(reverse('aristotle_help:help_base'))
        self.assertNotContains(response, "My very specific help page")

        response = self.client.get(reverse('aristotle_help:help_concepts'))
        self.assertNotContains(response, "Question")

        response = self.client.get(reverse('aristotle_help:concept_app_help', args=['extension_test']))
        self.assertTrue(response.status_code == 404)

        response = self.client.get(reverse('aristotle_help:concept_help', args=['extension_test', 'question']))
        self.assertTrue(response.status_code == 404)

    # -------------------------------------------

    def test_browse_visible_if_enabled(self):
        self.login_superuser()
        response = self.client.get(reverse('browse_apps'))
        self.assertContains(response, "Aristotle Test Suite for testing extensions")
        self.assertContains(response, "Question")

        response = self.client.get(reverse('browse_models', args=['extension_test']))
        self.assertContains(response, "Aristotle Test Suite for testing extensions")

        response = self.client.get(reverse('browse_concepts', args=['extension_test', 'question']))
        self.assertContains(response, "Question")
        self.assertContains(response, "Test Question Title")


    @override_settings(ARISTOTLE_SETTINGS=dict(
        settings.ARISTOTLE_SETTINGS,
        CONTENT_EXTENSIONS=BASE_ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'] + ['aristotle_mdr_links']
    ))
    def test_browse_not_visible_if_disabled(self):
        self.login_superuser()
        response = self.client.get(reverse('browse_apps'))
        self.assertNotContains(response, "Aristotle Test Suite for testing extensions")
        self.assertNotContains(response, "Question")

        response = self.client.get(reverse('browse_models', args=['extension_test']))
        self.assertTrue(response.status_code == 404)

        response = self.client.get(reverse('browse_concepts', args=['extension_test', 'question']))
        self.assertTrue(response.status_code == 404)

    # -------------------------------------------

    def test_search_option_visible_if_enabled(self):
        self.login_superuser()
        response = self.client.get(reverse('aristotle_mdr:search'))
        self.assertContains(response, "Question")

        response = self.client.get(reverse('aristotle_mdr:search')+"?q=Question Title")
        self.assertContains(response, "Some unique string")

    @override_settings(ARISTOTLE_SETTINGS=dict(
        settings.ARISTOTLE_SETTINGS,
        CONTENT_EXTENSIONS=BASE_ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'] + ['aristotle_mdr_links']
    ))
    def test_search_option_not_visible_if_disabled(self):
        self.login_superuser()
        response = self.client.get(reverse('aristotle_mdr:search'))
        self.assertNotContains(response, "Question")

        response = self.client.get(reverse('aristotle_mdr:search')+"?q=Question Title")
        self.assertNotContains(response, "Some unique string")

    # -------------------------------------------

    def test_object_indexable_if_enabled(self):
        from haystack.query import SearchQuerySet
        indexed_item = Question.objects.create(
            name="Different Question",
            definition="Some different unique string"
        )
        sqs = SearchQuerySet().auto_query("Different Question unique")
        self.assertTrue(indexed_item.pk in [s.object.pk for s in sqs])


    @override_settings(ARISTOTLE_SETTINGS=dict(
        settings.ARISTOTLE_SETTINGS,
        CONTENT_EXTENSIONS=BASE_ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'] + ['aristotle_mdr_links']
    ))
    def test_object_not_indexable_if_disabled(self):
        from haystack.query import SearchQuerySet

        from django.db.models.signals import pre_save
        from aristotle_mdr.models import check_concept_app_label
        pre_save.disconnect(check_concept_app_label)

        unindexed_item = Question.objects.create(
            name="Different Question",
            definition="Some different unique string"
        )
        pre_save.connect(check_concept_app_label)

        sqs = SearchQuerySet().auto_query("Different Question unique")
        self.assertTrue(unindexed_item.pk not in [s.object.pk for s in sqs])

    
    # -------------------------------------------

    def test_object_savable_if_enabled(self):
        created_item = Question.objects.create(
            name="Different Question",
            definition="Some different unique string"
        )
        self.assertTrue(Question.objects.filter(pk=created_item.pk))


    @override_settings(ARISTOTLE_SETTINGS=dict(
        settings.ARISTOTLE_SETTINGS,
        CONTENT_EXTENSIONS=BASE_ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'] + ['aristotle_mdr_links']
    ))
    def test_object_not_savable_if_disabled(self):
        from django.core.exceptions import ImproperlyConfigured
        from aristotle_mdr.models import _concept

        pre_count_c = _concept.objects.all().count()
        pre_count_q = Question.objects.count()

        with self.assertRaises(ImproperlyConfigured):
            uncreated_item = Question.objects.create(
                name="Different Question",
                definition="Some different unique string"
            )

        post_count_c = _concept.objects.all().count()
        post_count_q = Question.objects.count()
        self.assertTrue(post_count_c == pre_count_c)
        self.assertTrue(post_count_q == pre_count_q)

