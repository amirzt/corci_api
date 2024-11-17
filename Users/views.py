from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from Users.models import CustomUser, Country, City
from Users.serializers import RegisterSerializer, CountrySerializer, CitySerializer, ProfileSerializer
from django.core.validators import EmailValidator


class UsersViewSet(viewsets.ModelViewSet):

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
