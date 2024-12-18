from rest_framework import serializers

from Content.models import Content, Task
from notification.utils import send_notification
from .models import CustomUser, City, Country, Connection, Category, UserCategory, Banner, HomeMessage, Version


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = City
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField('get_skills')
    posts = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    connected = serializers.SerializerMethodField()
    request = serializers.SerializerMethodField()

    # city = CitySerializer(read_only=True)
    # city_id = serializers.PrimaryKeyRelatedField(
    #     queryset=City.objects.all(), write_only=True, source='city'
    # )

    @staticmethod
    def get_skills(self):
        categories = UserCategory.objects.filter(user=self)
        return UserCategorySerializer(categories, many=True).data

    @staticmethod
    def get_posts(self):
        return Content.objects.filter(user=self).count()

    @staticmethod
    def get_tasks(self):
        return Task.objects.filter(offer__user=self).count()

    def get_connected(self, obj):
        user = self.context.get('user', None)
        if user:
            return Connection.objects.filter(first_user=user,
                                             second_user=obj,
                                             accepted=True).exists()
        return False

    def get_request(self, obj):
        user = self.context.get('user', None)
        if user:
            return Connection.objects.filter(first_user=user,
                                             second_user=obj,
                                             accepted=False).exists()
        return False

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'user_name', 'phone', 'image', 'cover', 'bio', 'gender', 'date_joint',
                  'skills', 'credit', 'tasks', 'posts', 'connected', 'request']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def save(self, **kwargs):
        user = CustomUser(**self.validated_data)
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class ConnectionSerializer(serializers.ModelSerializer):
    first_user = ProfileSerializer(read_only=True)
    second_user = ProfileSerializer(read_only=True)

    class Meta:
        model = Connection
        fields = '__all__'


class AddConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ['second_user', 'level']

    def save(self, **kwargs):
        connection = Connection(first_user=self.context.get('user'),
                                **self.validated_data)
        connection.save()

        # send in app notif
        send_notification(receiver=connection.second_user, related_user=connection.first_user,
                          message_type='connection',
                          message='')

        return connection

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class UserCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = UserCategory
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'


class HomeMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeMessage
        fields = '__all__'


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = '__all__'
