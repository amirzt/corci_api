from rest_framework import serializers

from Content.serializers import ContentSerializer, OfferSerializer
from Users.serializers import ProfileSerializer
from notification.models import UserNotification


class UserNotificationSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)
    related_user = ProfileSerializer(read_only=True)
    content = ContentSerializer(read_only=True)
    offer = OfferSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = '__all__'
