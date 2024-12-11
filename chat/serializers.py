from rest_framework import serializers

from Content.serializers import OfferSerializer
from Users.serializers import ProfileSerializer
from .models import Chat, Message
from .utils import get_unread_message_count


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'offer', 'timestamp']


class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    second_user = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'last_message', 'unread_count', 'second_user']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        return MessageSerializer(last_message).data if last_message else None

    def get_unread_count(self, obj):
        return get_unread_message_count(self.context.get('user'), obj)

    def get_second_user(self, obj):
        request_user = self.context.get('user')
        # Get the other participant in the chat
        second_user = obj.participants.exclude(user=request_user).first()
        return ProfileSerializer(second_user.user).data if second_user else None


class ChatMessageSerializer(serializers.ModelSerializer):
    offer = OfferSerializer()
    my_message = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'offer', 'timestamp', 'my_message']

    def get_my_message(self, obj):
        request_user = self.context.get('user')
        return obj.sender == request_user
