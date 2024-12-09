from django.contrib import admin

from Content.models import Content, ContentImage, Like, Comment, Offer, Task

# Register your models here.
admin.site.register(Content)
admin.site.register(ContentImage)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Offer)
admin.site.register(Task)
