# Generated by Django 5.1.3 on 2024-12-10 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0007_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to='category/'),
        ),
    ]