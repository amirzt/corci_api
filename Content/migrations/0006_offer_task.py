# Generated by Django 5.1.3 on 2024-12-09 12:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Content', '0005_delete_responsible'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('due_date', models.DateTimeField(null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Content.content')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('canceled_by_author', 'Canceled by author'), ('canceled_buy_responsible', 'Canceled by responsible')], default='ongoing', max_length=50)),
                ('score', models.IntegerField(default=0)),
                ('author_comment', models.TextField(blank=True, max_length=1000, null=True)),
                ('responsible_comment', models.TextField(blank=True, max_length=1000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Content.offer')),
            ],
        ),
    ]
