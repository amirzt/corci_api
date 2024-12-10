from chat.models import Chat, ChatParticipant, Message


def get_or_create_chat_between_users(user1, user2):
    participant_ids = sorted([user1.id, user2.id])
    unique_identifier = "_".join(map(str, participant_ids))

    chat, created = Chat.objects.get_or_create(unique_identifier=unique_identifier)

    if created:
        chat.participants.set([user1, user2])

    return chat, created


def get_unread_message_count(user, chat):
    last_read_message_id = ChatParticipant.objects.get(user=user, chat=chat).last_read_message_id
    if last_read_message_id:
        return chat.messages.filter(id__gt=last_read_message_id).count()
    return chat.messages.count()


def mark_messages_as_read(user, chat):
    last_message = chat.messages.order_by('-timestamp').first()
    if last_message:
        ChatParticipant.objects.filter(user=user, chat=chat).update(last_read_message_id=last_message.id)


def send_message(sender, receiver, content, offer=None):

    from django.db import transaction

    chat, _ = get_or_create_chat_between_users(sender, receiver)

    with transaction.atomic():
        message = Message.objects.create(chat=chat, sender=sender, content=content)
        if offer:
            message.offer = offer
            message.save()
        # ChatParticipant.objects.filter(chat=chat, user=receiver).update(last_read_message_id=None)

    return message
