from django.contrib import admin

from Content.models import Content, ContentImage, Like

# Register your models here.
admin.site.register(Content)
admin.site.register(ContentImage)
admin.site.register(Like)
