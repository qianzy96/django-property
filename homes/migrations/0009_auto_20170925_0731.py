# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-25 07:31
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homes', '0008_seo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'Unpublished'), (1, 'Published')])),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.CharField(max_length=1000)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('action', models.URLField()),
                ('attachment', models.FileField(upload_to=b'banners/')),
            ],
        ),
        migrations.AlterModelOptions(
            name='seo',
            options={'verbose_name': 'SEO', 'verbose_name_plural': 'SEO'},
        ),
        migrations.AlterField(
            model_name='block',
            name='content',
            field=ckeditor.fields.RichTextField(),
        ),
    ]