from rest_framework import serializers

from Content.serializers import OfferSerializer
from .models import Chat, Message
from .utils import get_unread_message_count


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'offer', 'timestamp']


class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'last_message', 'unread_count']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        return MessageSerializer(last_message).data if last_message else None

    def get_unread_count(self, obj):
        return get_unread_message_count(self.context.get('user'), obj)


class ChatMessageSerializer(serializers.ModelSerializer):
    offer = OfferSerializer()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'offer', 'timestamp']
