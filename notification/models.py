from django.db import models

from Content.models import Content, Offer
from Users.models import CustomUser


class UserNotification(models.Model):
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='receiver')
    related_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='related_user')
    content = models.ForeignKey(Content, null=True, on_delete=models.SET_NULL)
    offer = models.ForeignKey(Offer, null=True, default=None, on_delete=models.SET_NULL)
    message = models.TextField(max_length=1000, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
