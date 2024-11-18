from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from Users.models import CustomUser, Country, City, Connection
from Users.serializers import RegisterSerializer, CountrySerializer, CitySerializer, ProfileSerializer, \
    ConnectionSerializer, AddConnectionSerializer
from django.core.validators import EmailValidator


class UsersViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        if email is None or password is None:
            return Response({'error': 'please enter your email and password'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validator = EmailValidator()
            validator(email)
            pass
        except ValidationError:
            return Response({'error': 'email is not valid'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            exist = True
            if not user.check_password(password):
                return Response({'error': 'password is not correct'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                exist = False
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key,
                         'exist': exist}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def country(self, request):
        country = Country.objects.all()
        serializer = CountrySerializer(country, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def city(self, request):
        city = City.objects.all()
        if 'country' in request.query_params:
            city = city.filter(country_id=request.query_params['country'])
        serializer = CitySerializer(city, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        if request.method == 'GET':
            if 'id' in request.query_params:
                user = CustomUser.objects.get(id=request.query_params['id'])
            else:
                user = CustomUser.objects.get(id=request.user.id)
            serializer = ProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PUT':
            user = CustomUser.objects.get(id=request.user.id)
            serializer = ProfileSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def get_queryset(self):
        first_user = Connection.objects.filter(first_user=self.get_user())
        return first_user

    def list(self, request, *args, **kwargs):
        category = self.request.query_params.get('category', None)
        if not category:
            return Response({'error': 'category is required'}, status=status.HTTP_400_BAD_REQUEST)

        if category == 'my_connections':
            queryset = Connection.objects.filter(first_user=self.get_user(),
                                                 accepted=True)
        else:
            queryset = Connection.objects.filter(second_user=self.get_user(),
                                                 accepted=False)

        if 'level' in request.query_params:
            queryset = queryset.filter(level=request.query_params['level'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = AddConnectionSerializer(data=request.data,
                                             context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        connection = self.get_object()
        if connection.first_user.id == request.user.id:
            connection.delete()
            return Response(status=status.HTTP_200_OK)
        return Response({'error': 'you can only delete your own connections'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        connection = self.get_object()
        if connection.first_user.id == request.user.id:
            serializer = AddConnectionSerializer(connection, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.update(connection, serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'you can only update your own connections'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def requests(self, request):
        user = self.get_user()
        connection = get_object_or_404(Connection, second_user=user, id=request.data.get('id'), accepted=False)
        accepted = request.data.get('accepted', None)
        if not accepted:
            return Response({'error': 'accepted is required'}, status=status.HTTP_400_BAD_REQUEST)
        if accepted == 'true':
            connection.accepted = True
            connection.save()

            new_connection = Connection(first_user=user, second_user=connection.first_user, level=connection.level,
                                        accepted=True)
            if 'level' in request.data:
                new_connection.level = request.data['level']
            new_connection.save()
            return Response(status=status.HTTP_200_OK)
        else:
            connection.delete()
            return Response(status=status.HTTP_200_OK)
