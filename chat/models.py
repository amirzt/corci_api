from django.db import models
import uuid

from Content.models import Offer
from Users.models import CustomUser


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unique_identifier = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
        verbose_name="Unique Identifier"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"

    def save(self, *args, **kwargs):
        # Generate a unique identifier for the chat
        if not self.unique_identifier:
            participant_ids = sorted(self.participants.values_list('id', flat=True))
            self.unique_identifier = "_".join(map(str, participant_ids))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Chat {self.unique_identifier}"


class ChatParticipant(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="chat_participations")
    last_read_message_id = models.UUIDField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("chat", "user")
        verbose_name = "Chat Participant"
        verbose_name_plural = "Chat Participants"

    def __str__(self):
        return f"{self.user.id} in Chat {self.chat.id}"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="messages_sent")
    content = models.TextField(max_length=1000, null=False, blank=False)
    image = models.ImageField(upload_to="messages/", null=True, blank=True)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"from {self.sender.id} in Chat {self.chat.id}"
