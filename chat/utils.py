from chat.models import Chat, ChatParticipant, Message


def get_or_create_chat_between_users(user1, user2):
    participant_ids = sorted([user1.id, user2.id])
    unique_identifier = "_".join(map(str, participant_ids))

    chat, created = Chat.objects.get_or_create(unique_identifier=unique_identifier)

    if created:
        ChatParticipant.objects.create(chat=chat, user=user1)
        ChatParticipant.objects.create(chat=chat, user=user2)

    return chat, created


def get_unread_message_count(user, chat):
    try:
        participant = ChatParticipant.objects.get(user=user, chat=chat)
    except ChatParticipant.DoesNotExist:
        return 0

    last_read_message_id = participant.last_read_message_id
    if not last_read_message_id:
        return chat.messages.exclude(sender=user).count()

    try:
        last_read_message = Message.objects.get(id=last_read_message_id)
        last_read_timestamp = last_read_message.timestamp
    except Message.DoesNotExist:
        return chat.messages.exclude(sender=user).count()

    unread_count = chat.messages.filter(
        timestamp__gt=last_read_timestamp
    ).exclude(sender=user).count()

    return unread_count


def mark_messages_as_read(user, chat):
    last_message = chat.messages.order_by('-timestamp').first()
    if last_message:
        ChatParticipant.objects.filter(user=user, chat=chat).update(last_read_message_id=last_message.id)

    Message.objects.filter(
        chat=chat,
        is_read=False
    ).exclude(sender=user).update(is_read=True)


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
