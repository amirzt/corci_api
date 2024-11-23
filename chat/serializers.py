from rest_framework import serializers

from Users.serializers import ProfileSerializer
from chat.models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = ProfileSerializer()

    class Meta:
        model = Message
        fields = '__all__'


class AddMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content', 'image']

    def create(self, validated_data):
        message = Message.objects.create(**validated_data,
                                         user=self.context.get('user'))
        return message


class ChatSerializer(serializers.ModelSerializer):
    first_user = ProfileSerializer()
    second_user = ProfileSerializer()

    class Meta:
        model = Chat
        fields = '__all__'
