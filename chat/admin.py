from django.contrib import admin

from chat.models import Chat, Message, ChatParticipant

# Register your models here.
admin.site.register(Chat)
admin.site.register(ChatParticipant)
admin.site.register(Message)
