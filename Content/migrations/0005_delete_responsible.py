# Generated by Django 5.1.3 on 2024-12-09 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Content', '0004_comment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Responsible',
        ),
    ]