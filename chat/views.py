from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Users.models import CustomUser
from chat.models import Chat, ChatParticipant
from chat.serializers import ChatSerializer, ChatMessageSerializer
from chat.utils import send_message, mark_messages_as_read, get_unread_message_count


class ChatViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def list(self, request):
        user = self.get_user()
        participant_chats = ChatParticipant.objects.filter(user=user).values_list('chat', flat=True)
        chats = Chat.objects.filter(id__in=participant_chats)

        serializer = ChatSerializer(chats, many=True,
                                    context={'user': user})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def messages(self, request, pk=None):
        user = self.get_user()
        try:
            chat = Chat.objects.prefetch_related('participants').get(id=pk)
            if not chat.participants.filter(user_id=user.id).exists():
                raise PermissionDenied("You do not have permission to access this chat.")
        except Chat.DoesNotExist:
            return Response({"detail": "Chat not found or access denied."}, status=404)

        messages = chat.messages.order_by('timestamp')
        serializer = ChatMessageSerializer(messages, many=True,
                                           context={"user": user})

        # read messages
        mark_messages_as_read(user, chat)

        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def send_message(self, request):
        sender = self.get_user()

        receiver_id = request.data.get('receiver_id')
        content = request.data.get('content')
        offer = request.data.get('offer', None)

        if not receiver_id:
            raise ValidationError({"receiver_id": "This field is required."})
        if not content:
            raise ValidationError({"content": "This field is required."})

        receiver = get_object_or_404(CustomUser, id=receiver_id)

        try:
            message = send_message(sender=sender, receiver=receiver, content=content, offer=offer)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ChatMessageSerializer(message, context={"user": sender})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='unread_count', url_name='unread_count')
    def unread_count(self, request):
        user = self.get_user()

        participant_chats = ChatParticipant.objects.filter(user=user).values_list('chat', flat=True)

        total_unread_count = 0
        for chat_id in participant_chats:
            chat = Chat.objects.get(id=chat_id)
            total_unread_count += get_unread_message_count(user, chat)

        return Response({"unread_count": total_unread_count}, status=status.HTTP_200_OK)
