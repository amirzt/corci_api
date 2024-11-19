from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Content.models import Content, ContentImage
from Content.serializers import ContentSerializer, AddContentSerializer, AddContentImageSerializer
from Users.models import CustomUser, Connection


class ContentViewSet(viewsets.ModelViewSet):
    # queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'type', 'urgency', 'circle', 'due_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return ContentSerializer
        return AddContentSerializer

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def get_queryset(self):
        hierarchy = {
            'level_1': 1,
            'level_2': 2,
            'level_3': 3,
            'public': 4,
        }

        connections = Connection.objects.filter(
            first_user=self.get_user(),
            accepted=True
        ).select_related('second_user')

        visible_contents = Content.objects.filter(
            Q(circle='public') |  # Public contents are always visible
            Q(
                user__in=[conn.second_user for conn in connections],
                circle__in=[
                    circle for circle, level in hierarchy.items()
                    if any(hierarchy[circle] <= hierarchy[conn.level] for conn in connections)
                ]
            )
        )

        return visible_contents

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={'user': self.get_user()})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        content = get_object_or_404(Content, id=kwargs['pk'])
        if content.user.id == request.user.id:
            content.delete()
            return Response(status=status.HTTP_200_OK)
        return Response({'error': 'you can only delete your own contents'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        content = get_object_or_404(Content, id=kwargs['pk'])
        if content.user.id == request.user.id:
            serializer = AddContentSerializer(content, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.update(content, serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'you can only update your own contents'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def images(self, request):
        if request.method == 'POST':
            user = get_object_or_404(CustomUser, id=request.user.id)
            content = get_object_or_404(Content, id=request.data['content'])
            if content.user.id != user.id:
                return Response({'error': 'you can only add images to your own contents'},
                                status=status.HTTP_403_FORBIDDEN)

            serializer = AddContentImageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(content=content)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user = get_object_or_404(CustomUser, id=request.user.id)
            image = get_object_or_404(ContentImage, id=request.data['id'])
            if image.content.user.id != user.id:
                return Response({'error': 'you can only delete images from your own contents'},
                                status=status.HTTP_403_FORBIDDEN)

            image.delete()
            return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        user = self.get_user()
        contents = Content.objects.filter(user=user)
        serializer = ContentSerializer(contents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
