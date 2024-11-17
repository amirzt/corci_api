from rest_framework import serializers
from .models import CustomUser, City, Country, Connection


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
    city = CitySerializer(read_only=True)  # Nested serializer for GET
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), write_only=True, source='city'
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'city', 'city_id', 'name', 'email', 'user_name', 'phone', 'image', 'cover', 'bio', 'gender']

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
        return connection
