from rest_framework import serializers

from Content.models import Content, ContentImage, Like, Responsible
from Users.serializers import CategorySerializer, ProfileSerializer


class AddContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['description', 'circle', 'type', 'urgency', 'category', 'due_date', 'priceless']

    def save(self, **kwargs):
        content = Content(**self.validated_data,
                          user=self.context.get('user'))
        content.save()
        return content

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AddContentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentImage
        fields = ['image', 'content']

    def save(self, **kwargs):
        content_image = ContentImage(**self.validated_data)
        content_image.save()
        return content_image


class ContentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentImage
        fields = '__all__'


class ContentSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = serializers.SerializerMethodField('get_images')
    liked = serializers.SerializerMethodField('get_liked')

    def get_liked(self, obj):
        user = self.context.get('user')
        if user:
            return Like.objects.filter(content=obj, user=user).exists()
        return False

    @staticmethod
    def get_images(obj):
        return ContentImageSerializer(ContentImage.objects.filter(content=obj), many=True).data

    class Meta:
        model = Content
        fields = '__all__'


class ResponsibleSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)
    content = ContentSerializer(read_only=True)

    class Meta:
        model = Responsible
        fields = '__all__'
