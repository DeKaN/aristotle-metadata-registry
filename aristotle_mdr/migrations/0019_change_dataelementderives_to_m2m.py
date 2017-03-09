# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-10 04:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0018_improve_request_reviews'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataelementderivation',
            name='derives',
        ),
        migrations.AddField(
            model_name='dataelementderivation',
            name='derives',
            field=models.ManyToManyField(blank=True, help_text='binds with one or more output Data_Elements that are the result of the application of the Data_Element_Derivation.', null=True, related_name='derived_from', to='aristotle_mdr.DataElement'),
        ),
    ]
