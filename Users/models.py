from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from Users.managers import CustomUserManager


class Country(models.Model):
    name = models.CharField(max_length=50, null=True, blank=False)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50, null=True, blank=False)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class GenderChoices(models.TextChoices):
        MALE = 'male'
        FEMALE = 'female'
        Nonbinary = 'nonbinary'
        OTHER = 'other'

    name = models.CharField(max_length=50, null=True, blank=False)
    user_name = models.CharField(max_length=50, null=True, blank=False, unique=True)
    phone = models.CharField(max_length=11, null=False, blank=False)
    email = models.EmailField(null=False, blank=False, unique=True)
    image = models.ImageField(upload_to='user/image/', null=True, blank=True)
    cover = models.ImageField(upload_to='user/cover/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True, max_length=1000)
    gender = models.CharField(max_length=50, null=True, blank=True, choices=GenderChoices.choices,
                              default=GenderChoices.OTHER)

    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    date_joint = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    version = models.CharField(default='1.0.0', max_length=20)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Connection(models.Model):
    class ConnectionLevel(models.TextChoices):
        level_1 = 'level_1', '1'
        level_2 = 'level_2', '2'
        level_3 = 'level_3', '3'

    first_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='first_user')
    second_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='second_user')
    level = models.CharField(max_length=10, choices=ConnectionLevel.choices, default=ConnectionLevel.level_1)
    accepted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_user} - {self.second_user}'


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, default=None, max_length=1000)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
