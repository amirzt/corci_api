from django.db import models

from Content.models import Offer
from Users.models import CustomUser


# Create your models here.
class Chat(models.Model):
    first_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='first')
    second_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='second')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('first_user', 'second_user')

    def __str__(self):
        return f'{self.first_user} - {self.second_user}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='chat/image/', null=True, blank=True)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sender}'
