from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
import aristotle_mdr.tests.utils as utils
from django.core.exceptions import PermissionDenied

from django.test.utils import setup_test_environment
setup_test_environment()

# This is for testing permissions around RA mangement.

class RACreationTests(utils.LoggedInViewPages,TestCase):
    def test_anon_cannot_create(self):
        self.logout()
        response = self.client.get(reverse('aristotle:registrationauthority_create'))
        self.assertRedirects(response,
            reverse("friendly_login",)+"?next="+
            reverse('aristotle:registrationauthority_create')
            )

    def test_viewer_cannot_create(self):
        self.login_viewer()

        response = self.client.get(reverse('aristotle:registrationauthority_create'))
        self.assertEqual(response.status_code, 403)

        before_count = models.RegistrationAuthority.objects.count()
        response = self.client.post(
            reverse('aristotle:registrationauthority_create'),
            {
                'name':"My cool team",
                'definition':"This team rocks!"
            }
        )
        self.assertEqual(response.status_code, 403)
        after_count = models.RegistrationAuthority.objects.count()
        self.assertEqual(after_count, before_count)

    def test_manager_cannot_create(self):
        self.login_manager()

        response = self.client.get(reverse('aristotle:registrationauthority_create'))
        self.assertEqual(response.status_code, 403)

        before_count = models.RegistrationAuthority.objects.count()
        response = self.client.post(
            reverse('aristotle:registrationauthority_create'),
            {
                'name':"My cool team",
                'definition':"This team rocks!"
            }
        )
        self.assertEqual(response.status_code, 403)
        after_count = models.RegistrationAuthority.objects.count()
        self.assertEqual(after_count, before_count)

    def test_registry_owner_can_create(self):
        self.login_superuser()

        response = self.client.get(reverse('aristotle:registrationauthority_create'))
        self.assertEqual(response.status_code, 200)

        before_count = models.RegistrationAuthority.objects.count()
        response = self.client.post(
            reverse('aristotle:registrationauthority_create'),
            {
                'name':"My cool registrar",
                'definition':"This RA rocks!"
            },
            follow=True
        )
        self.assertTrue(response.redirect_chain[0][1] == 302)

        self.assertEqual(response.status_code, 200)
        after_count = models.RegistrationAuthority.objects.count()
        self.assertEqual(after_count, before_count + 1)

        new_ra = response.context['item']

        self.assertEqual(new_ra.name, "My cool registrar")
        self.assertEqual(new_ra.definition, "This RA rocks!")



class RAUpdateTests(utils.LoggedInViewPages,TestCase):
    def test_anon_cannot_update(self):
        self.logout()
        response = self.client.get(reverse('aristotle:registrationauthority_create'))
        self.assertRedirects(response,
            reverse("friendly_login",)+"?next="+
            reverse('aristotle:registrationauthority_create')
            )

    def test_viewer_cannot_update(self):
        self.login_viewer()

        my_ra = models.RegistrationAuthority.objects.create(name="My new RA", definition="")

        response = self.client.get(reverse('aristotle:registrationauthority_edit', args=[my_ra.pk]))
        self.assertEqual(response.status_code, 403)

        data = {
            'name':"My cool registrar",
            'definition':"This RA rocks!"
        }

        response = self.client.post(
            reverse('aristotle:registrationauthority_edit', args=[my_ra.pk]),
            data
        )
        self.assertEqual(response.status_code, 403)
        my_ra = models.RegistrationAuthority.objects.get(pk=my_ra.pk)

        self.assertNotEqual(my_ra.name, "My cool registrar")
        self.assertNotEqual(my_ra.definition, "This RA rocks!")

    def test_registry_owner_can_edit(self):
        self.login_superuser()

        my_ra = models.RegistrationAuthority.objects.create(name="My new RA", definition="")

        response = self.client.get(reverse('aristotle:registrationauthority_edit', args=[my_ra.pk]))
        self.assertEqual(response.status_code, 200)
        
        data = response.context['form'].initial
        data.update({
            'name':"My cool registrar",
            'definition':"This RA rocks!"
        })

        response = self.client.post(
            reverse('aristotle:registrationauthority_edit', args=[my_ra.pk]),
            data
        )
        self.assertEqual(response.status_code, 302)
        my_ra = models.RegistrationAuthority.objects.get(pk=my_ra.pk)

        self.assertEqual(my_ra.name, "My cool registrar")
        self.assertEqual(my_ra.definition, "This RA rocks!")

    def test_ramanager_can_edit(self):
        self.login_ramanager()

        my_ra = models.RegistrationAuthority.objects.create(name="My new RA", definition="")

        response = self.client.get(reverse('aristotle:registrationauthority_edit', args=[my_ra.pk]))
        self.assertEqual(response.status_code, 403)

        my_ra.managers.add(self.ramanager)
        my_ra = models.RegistrationAuthority.objects.get(pk=my_ra.pk)
        self.assertTrue(self.ramanager in my_ra.managers.all())

        response = self.client.get(reverse('aristotle:registrationauthority_edit', args=[my_ra.pk]))
        self.assertEqual(response.status_code, 200)

        data = response.context['form'].initial
        data.update({
            'name':"My cool registrar",
            'definition':"This RA rocks!",
        })

        response = self.client.post(
            reverse('aristotle:registrationauthority_edit', args=[my_ra.pk]),
            data
        )
        self.assertEqual(response.status_code, 302)
        my_ra = models.RegistrationAuthority.objects.get(pk=my_ra.pk)

        self.assertEqual(my_ra.name, "My cool registrar")
        self.assertEqual(my_ra.definition, "This RA rocks!")


class RAListTests(utils.LoggedInViewPages,TestCase):
    def test_anon_cannot_create(self):
        self.logout()
        response = self.client.get(reverse('aristotle:registrationauthority_list'))
        self.assertRedirects(response,
            reverse("friendly_login",)+"?next="+
            reverse('aristotle:registrationauthority_list')
            )

    def test_viewer_cannot_list(self):
        self.login_viewer()

        response = self.client.get(reverse('aristotle:registrationauthority_list'))
        self.assertEqual(response.status_code, 403)

    def test_ramanager_cannot_list(self):
        self.login_ramanager()

        response = self.client.get(reverse('aristotle:registrationauthority_list'))
        self.assertEqual(response.status_code, 403)

    def test_registry_owner_can_list(self):
        self.login_superuser()

        response = self.client.get(reverse('aristotle:registrationauthority_list'))
        self.assertEqual(response.status_code, 200)



class RAManageTests(utils.LoggedInViewPages,TestCase):
    def test_anon_cannot_create(self):
        self.logout()
        response = self.client.get(reverse('aristotle:registrationauthority_manage', args=[self.ra.pk]))
        self.assertRedirects(response,
            reverse("friendly_login",)+"?next="+
            reverse('aristotle:registrationauthority_manage', args=[self.ra.pk])
            )

    def test_viewer_cannot_view_manage(self):
        self.login_viewer()

        response = self.client.get(reverse('aristotle:registrationauthority_manage', args=[self.ra.pk]))
        self.assertEqual(response.status_code, 403)

    def test_ramanager_can_view_manage(self):
        self.login_ramanager()

        response = self.client.get(reverse('aristotle:registrationauthority_manage', args=[self.ra.pk]))
        self.assertEqual(response.status_code, 200)

        self.ra.managers.remove(self.ramanager)
        self.ra = models.RegistrationAuthority.objects.get(pk=self.ra.pk)
        response = self.client.get(reverse('aristotle:registrationauthority_manage', args=[self.ra.pk]))
        self.assertEqual(response.status_code, 403)

    def test_registry_owner_can_view_manage(self):
        self.login_superuser()

        response = self.client.get(reverse('aristotle:registrationauthority_manage', args=[self.ra.pk]))
        self.assertEqual(response.status_code, 200)
