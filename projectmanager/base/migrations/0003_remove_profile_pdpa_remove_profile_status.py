# Generated by Django 4.1.5 on 2024-10-17 23:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_profile_department_alter_profile_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='pdpa',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='status',
        ),
    ]