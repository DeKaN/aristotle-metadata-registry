from django.test import TestCase

import aristotle_mdr.tests.utils as utils
from aristotle_mdr.models import ObjectClass, Workgroup
from django.core.urlresolvers import reverse

from aristotle_mdr.tests.main.test_bulk_actions import BulkActionsTest
from aristotle_mdr import models

from django.test.utils import setup_test_environment
setup_test_environment()


class TestBulkActions(BulkActionsTest, TestCase):
    def setUp(self):
        super(TestBulkActions, self).setUp()
        self.item = ObjectClass.objects.create(
            name="Test Object",
            workgroup=self.wg1,
        )
        self.su.profile.favourites.add(self.item)

    def test_incomplete_action_exists(self):
        self.login_superuser()
        response = self.client.get(reverse('aristotle:userFavourites'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'incomplete action')

class TestDeleteBulkAction(BulkActionsTest, TestCase):

    def test_delete_by_superuser(self):
        self.login_superuser()

        self.assertTrue(self.su.is_staff)

        num_items = ObjectClass.objects.count()
        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'bulk_actions_test.actions.StaffDeleteActionForm',
                'safe_to_delete': True,
                'items': [self.item1.id, self.item2.id],
            }
        )
        self.assertContains(response, 'Use this page to confirm you wish to delete the following items')

        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'bulk_actions_test.actions.StaffDeleteActionForm',
                'safe_to_delete': True,
                'items': [self.item1.id, self.item2.id],
                "confirmed": True
            }
        )
        self.assertEqual(num_items - 2, ObjectClass.objects.count())

    def test_delete_by_editor(self):
        
        self.editor.is_staff = False
        self.editor.save()
        self.editor = self.editor.__class__.objects.get(pk=self.editor.pk)  # decache
        self.assertFalse(self.editor.is_staff)
        self.login_editor()

        num_items = ObjectClass.objects.count()
        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'bulk_actions_test.actions.StaffDeleteActionForm',
                'safe_to_delete': True,
                'items': [self.item1.id, self.item2.id],
            },
            follow=True
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'bulk_actions_test.actions.StaffDeleteActionForm',
                'safe_to_delete': True,
                'items': [self.item1.id, self.item2.id],
                "confirmed": True
            }
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(num_items, ObjectClass.objects.count())



class BulkDownloadTests(BulkActionsTest, TestCase):
    download_type="txt"

    def test_bulk_txt_download_on_permitted_items(self):
        self.login_editor()

        self.assertEqual(self.editor.profile.favourites.count(), 0)
        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_mdr.forms.bulk_actions.BulkDownloadForm',
                'items': [self.item1.id, self.item2.id],
                "title": "The title",
                "download_type": self.download_type,
                'confirmed': 'confirmed',
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_bulk_txt_download_on_forbidden_items(self):
        self.login_editor()

        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_mdr.forms.bulk_actions.BulkDownloadForm',
                'items': [self.item1.id, self.item4.id],
                "title": "The title",
                "download_type": self.download_type,
                'confirmed': 'confirmed',
            },
            follow=True
        )
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][1], 302)


    def test_bulk_txt_download_on_forbidden_items_by_anonymous_user(self):
        self.logout()

        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_mdr.forms.bulk_actions.BulkDownloadForm',
                'items': [self.item1.id, self.item4.id],
                "title": "The title",
                "download_type": self.download_type,
                'confirmed': 'confirmed',
            },
            follow=True
        )
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][1], 302)

        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_mdr.forms.bulk_actions.BulkDownloadForm',
                'items': [self.item1.id, self.item4.id],
                "title": "The title",
                "download_type": self.download_type,
                'confirmed': 'confirmed',
            },
        )
        self.assertRedirects(
            response,
            reverse(
                'aristotle:bulk_download',
                kwargs={
                    "download_type": self.download_type,
                }
            )+"?title=The%20title"+"&items=%s&items=%s"%(self.item1.id, self.item4.id)
        )

    def test_content_exists_in_bulk_txt_download_on_permitted_items(self):
        self.login_editor()

        self.item5 = models.DataElementConcept.objects.create(name="DEC1", definition="DEC5 definition", objectClass=self.item2, workgroup=self.wg1)

        response = self.client.get(
            reverse(
                'aristotle:bulk_download',
                kwargs={
                    "download_type": self.download_type,
                }
            ),
            {
                "items": [self.item1.id, self.item5.id],
                "title": "The title",
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item1.name)
        self.assertContains(response, self.item2.name)  # Will be in as its a component of DEC5
        self.assertContains(response, self.item5.name)

        self.assertContains(response, self.item1.definition)
        self.assertContains(response, self.item2.definition)  # Will be in as its a component of DEC5
        self.assertContains(response, self.item5.definition)

