# Generated by Django 4.1.3 on 2022-12-22 01:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonDRF', '0002_rename_tittle_category_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menuitem',
            old_name='tittle',
            new_name='title',
        ),
    ]