from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Content.models import Content, ContentImage, Like, Comment, Offer, Task
from Content.serializers import ContentSerializer, AddContentSerializer, AddContentImageSerializer, \
    CommentSerializer, AddCommentSerializer, OfferSerializer, AddOfferSerializer, TaskSerializer
from Users.models import CustomUser, Connection, UserCategory
from chat.utils import send_message
from notification.utils import send_notification


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
    def posts(self, request):
        if 'user' in request.query_params:
            user = get_object_or_404(CustomUser, id=request.query_params.get('user'))
        else:
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


class OfferViewSet(ContentViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['content', 'status', 'due_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return OfferSerializer
        return AddOfferSerializer

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def get_queryset(self):
        offers = Offer.objects.filter(content__user=self.get_user()).select_related()
        return offers

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        offer = Offer.objects.filter(user=self.get_user(),
                                     content=request.data['content']).count()
        if offer > 0:
            return Response(data={"message": "You have already sent your offer"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data,
                                         partial=True,
                                         context={'user': self.get_user()})
        if serializer.is_valid():
            offer = serializer.save()
            # send chat message
            send_message(sender=self.get_user(), receiver=offer.content.user, content=offer.description, offer=offer)

            # send in app notif
            send_notification(receiver=offer.content.user, content=offer.content, message_type='offer', offer=offer,
                              message='')

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        offer = get_object_or_404(Offer, id=kwargs['pk'])
        if offer.content.user == self.get_user():
            new_status = request.data.get('status', None)
            if not new_status:
                return Response({'error': 'you must specify status'}, status=status.HTTP_400_BAD_REQUEST)
            offer.status = new_status
            offer.save()

            # create task
            if offer.status == Offer.Status.accepted:
                task = Task.objects.create(offer=offer,
                                           due_date=offer.due_date)
                task.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'error': 'you can only update your own offers'}, status=status.HTTP_400_BAD_REQUEST)


def calculate_score(task):
    if task.offer.content.category:
        category = task.offer.content.category
        responsible = task.offer.user
        skill, created = UserCategory.objects.get_or_create(category=category,
                                                            user=responsible)
        if skill.score == 0:
            skill.score = float(task.score)
        else:
            skill.score = (float(skill.score) + float(task.score)) / 2
        skill.save()


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['due_date']

    def get_serializer_class(self):
        return TaskSerializer

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def get_queryset(self):
        response = Task.objects.filter(offer__user=self.get_user()).select_related()
        own = Task.objects.filter(offer__content__user=self.get_user()).select_related()
        tasks = response | own
        return tasks

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=kwargs['pk'])
        if task.offer.user == self.get_user() or task.offer.content.user == self.get_user():
            if task.status == Task.Status.completed:
                return Response({'error': 'this task is completed'}, status=status.HTTP_400_BAD_REQUEST)
            new_status = request.data.get('status', None)
            if not new_status:
                return Response({'error': 'you must specify status'}, status=status.HTTP_400_BAD_REQUEST)
            if 'score' in request.data:
                task.score = request.data.get('score')
            if 'author_comment' in request.data:
                task.author_comment = request.data.get('author_comment')
            if 'responsible_comment' in request.data:
                task.responsible_comment = request.data.get('responsible_comment')
            task.status = new_status
            task.save()

            if new_status == Task.Status.completed:
                calculate_score(task)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'error': 'you can only update your own tasks'}, status=status.HTTP_400_BAD_REQUEST)
