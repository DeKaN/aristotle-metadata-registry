from django.apps import apps
from django.test import TestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
import aristotle_mdr.tests.utils as utils
from django.db import connection

import unittest


@unittest.skipIf(connection.vendor in ['microsoft', 'mssql'], "MSSQL Doesn't support temporarily disabling foreign key constraints")
class BaseMigrations(object):
    """
    Thanks to: https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
    """

    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name

    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass

@unittest.skipIf(connection.vendor in ['microsoft', 'mssql'], "MSSQL Doesn't support temporarily disabling foreign key constraints")
class TestUUIDMigration(BaseMigrations, TestCase):

    migrate_from = '0022_switch_to_concept_relations'
    migrate_to = '0024_add_uuid_instances'

    def setUpBeforeMigration(self, apps):

        DataElement = apps.get_model('aristotle_mdr', 'DataElement')
        self.obj = DataElement.objects.create(
            name = "Some data",
            definition = "",
        )
        self.before_uuid = self.obj.uuid

        self.before_pk = self.obj.pk

    def test_tags_migrated(self):
        DataElement = apps.get_model('aristotle_mdr', 'DataElement')
        UUID = apps.get_model('aristotle_mdr', 'UUID')
        
        my_uuid = UUID.objects.get(uuid=self.before_uuid)
        my_obj = DataElement.objects.get(pk=self.before_pk)

        self.assertEqual(my_obj.uuid, my_uuid)
