from django.db import models

from Users.models import CustomUser, Category


class Content(models.Model):
    class TypeChoice(models.TextChoices):
        offer = 'offer', 'Offer'
        request = 'request', 'Request'
        post = 'post', 'Post'

    class UrgencyChoices(models.TextChoices):
        low = 'low', 'Low'
        medium = 'medium', 'Medium'
        high = 'high', 'High'

    class Circle(models.TextChoices):
        level_1 = 'level_1', '1'
        level_2 = 'level_2', '2'
        level_3 = 'level_3', '3'
        public = 'public', 'Public'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=50, choices=TypeChoice.choices, default=TypeChoice.post)
    due_date = models.DateTimeField(null=True)
    urgency = models.CharField(max_length=50, choices=UrgencyChoices.choices, default=UrgencyChoices.low)
    circle = models.CharField(max_length=50, choices=Circle.choices, default=Circle.level_1)
    description = models.TextField(null=False, blank=False, max_length=1000)
    priceless = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    total_likes = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category.name


class ContentImage(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='content/image/', null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content.user.email