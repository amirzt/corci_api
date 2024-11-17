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
