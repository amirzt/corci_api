from rest_framework import serializers

from Content.serializers import OfferSerializer
from .models import Chat, Message, ChatParticipant


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'offer', 'timestamp']


class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'last_message']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        return MessageSerializer(last_message).data if last_message else None


class ChatMessageSerializer(serializers.ModelSerializer):
    offer = OfferSerializer()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'offer', 'timestamp']
