# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-31 02:20
from __future__ import unicode_literals

import aristotle_mdr.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr_identifiers', '0002_auto_20161124_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scopedidentifier',
            name='concept',
            field=aristotle_mdr.fields.ConceptForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identifiers', to='aristotle_mdr._concept'),
        ),
    ]
