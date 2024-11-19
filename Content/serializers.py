from rest_framework import serializers

from Content.models import Content, ContentImage
from Users.serializers import CategorySerializer


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

    @staticmethod
    def get_images(obj):
        return ContentImageSerializer(ContentImage.objects.filter(content=obj), many=True).data

    class Meta:
        model = Content
        fields = '__all__'
