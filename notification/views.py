from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from Users.models import CustomUser
from notification.models import UserNotification
from notification.serializers import UserNotificationSerializer


class UserNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = [UserNotificationSerializer]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_read', ]

    def get_serializer_class(self):
        return UserNotificationSerializer

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def get_queryset(self):
        notifications = UserNotification.objects.filter(receiver=self.get_user()).order_by('-created_at')
        return notifications

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        notification = get_object_or_404(UserNotification, id=kwargs['pk'])
        notification.is_read = True
        notification.save()
        return Response(status=status.HTTP_200_OK)
