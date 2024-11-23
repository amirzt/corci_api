from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Users.models import CustomUser
from chat.models import Chat, Message
from chat.serializers import ChatSerializer, AddMessageSerializer, MessageSerializer


class ChatViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def get_queryset(self):
        return Chat.objects.filter(second_user=self.request.user) | Chat.objects.filter(first_user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True,
                                         context={'user': self.get_user()})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def send(self, request):
        first_user = self.request.user
        second_user = get_object_or_404(CustomUser, id=request.data['second_user'])
        chat = Chat.objects.filter(first_user=first_user, second_user=second_user).first()
        if not chat:
            chat = Chat.objects.create(first_user=first_user, second_user=second_user)

        serializer = AddMessageSerializer(data=request.data, context={'user': first_user, 'chat': chat})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def messages(self, request):
        chat = get_object_or_404(Chat, id=request.query_params['chat'])
        messages = Message.objects.filter(chat=chat)
        serializer = MessageSerializer(messages, many=True, context={'user': self.get_user()})
        return Response(serializer.data, status=status.HTTP_200_OK)
