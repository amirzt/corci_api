from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Content.models import Content, ContentImage, Like, Responsible, Comment
from Content.serializers import ContentSerializer, AddContentSerializer, AddContentImageSerializer, \
    ResponsibleSerializer, CommentSerializer, AddCommentSerializer
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
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(Q(description__icontains=search))
        serializer = self.get_serializer(queryset, many=True,
                                         context={'user': self.get_user()})
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
        serializer = ContentSerializer(contents, many=True,
                                       context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request):
        content = get_object_or_404(Content, id=request.data['content'])
        like, created = Like.objects.get_or_create(user=self.get_user(), content=content)
        if created:
            like.save()
            content.total_likes += 1
            content.save()
            return Response(status=status.HTTP_200_OK)
        content.total_likes -= 1
        content.save()
        like.delete()
        return Response(status=status.HTTP_200_OK)


class ResponsibleViewSet(viewsets.ModelViewSet):
    queryset = Responsible.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ResponsibleSerializer

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def get_queryset(self):
        return Responsible.objects.filter(user=self.get_user())

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True,
                                         context={'user': self.get_user()})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        content = get_object_or_404(Content, id=request.data['content'])
        if content.user.id == request.user.id:
            return Response({'error': 'you cannot be responsible for your own content'},
                            status=status.HTTP_400_BAD_REQUEST)

        responsible, created = Responsible.objects.get_or_create(user=self.get_user(), content=content)
        return Response(status=status.HTTP_200_OK, data={'id': responsible.id})

    def destroy(self, request, *args, **kwargs):
        responsible = get_object_or_404(Responsible, id=kwargs['pk'])
        if responsible.user.id == request.user.id:
            responsible.delete()
            return Response(status=status.HTTP_200_OK)
        return Response({'error': 'you can only delete your own responsibilities'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def filter(self, request):
        user = self.get_user()

        if 'content' in self.request.query_params:
            print(self.request.query_params['content'])
            content = get_object_or_404(Content, id=self.request.query_params['content'])
            responsibilities = Responsible.objects.filter(content=content)
            serializer = ResponsibleSerializer(responsibilities, many=True,
                                               context={'user': user})
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif 'user' in self.request.query_params:
            second_user = get_object_or_404(CustomUser, id=self.request.query_params['user'])
            responsibilities = Responsible.objects.filter(user=second_user)
            serializer = ResponsibleSerializer(responsibilities, many=True,
                                               context={'user': user})
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif 'mine' in self.request.query_params:
            responsibilities = Responsible.objects.filter(content__user=user)
            serializer = ResponsibleSerializer(responsibilities, many=True,
                                               context={'user': user})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'you must specify content or user'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        responsible = get_object_or_404(Responsible, id=kwargs['pk'])
        content = responsible.content

        if content.status != 'pending':
            return Response({'error': 'you can only update responsibilities for pending contents'},
                            status=status.HTTP_400_BAD_REQUEST)

        if responsible.content.user.id == request.user.id:
            responsible.status = request.data['status']
            responsible.save()
            return Response(status=status.HTTP_200_OK)
        return Response({'error': 'you can only update your own content'}, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def list(self, request, *args, **kwargs):
        pk = request.query_params.get('content', None)
        if pk is None:
            return Response({'error': 'you must specify content id'}, status=status.HTTP_400_BAD_REQUEST)
        content = get_object_or_404(Content, id=pk)
        comments = Comment.objects.filter(content=content)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = self.get_user()
        serializer = AddCommentSerializer(data=request.data,
                                          context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
