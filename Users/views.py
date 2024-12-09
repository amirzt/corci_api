from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from Users.models import CustomUser, Country, City, Connection, Category, UserCategory, HomeMessage, Banner, Version, \
    UserFCMToken, OTP
from Users.serializers import RegisterSerializer, CountrySerializer, CitySerializer, ProfileSerializer, \
    ConnectionSerializer, AddConnectionSerializer, CategorySerializer, HomeMessageSerializer, BannerSerializer, \
    VersionSerializer
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

        # save fcm token
        fcm_token = request.data.get('fcm_token', None)
        if fcm_token:
            UserFCMToken.objects.create(user=user, token=fcm_token)

        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key,
                         'exist': exist}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def check_otp(self, request):
        email = request.data.get('email', None)
        user_otp = request.data.get('otp', None)
        if email is None or user_otp is None:
            return Response({'error': 'please enter your email and otp'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validator = EmailValidator()
            validator(email)
            pass
        except ValidationError:
            return Response({'error': 'email is not valid'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            otp = OTP.objects.filter(user=user).order_by('-created_at').first()
            if otp.otp != user_otp:
                return Response({'error': 'Code is not correct'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'user does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()

        # save fcm token
        fcm_token = request.data.get('fcm_token', None)
        if fcm_token:
            UserFCMToken.objects.create(user=user, token=fcm_token)

        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key}, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def splash(self, request):
        user = get_object_or_404(CustomUser, id=request.user.id)
        version = request.data.get('version', None)
        if version:
            user.version = version
            user.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def home(self, request):
        home_messages = HomeMessage.objects.filter(is_active=True).order_by('-created_at')
        banners = Banner.objects.filter(is_active=True).order_by('-created_at')
        version = Version.objects.all().last()

        return Response({
            'home_messages': HomeMessageSerializer(home_messages, many=True).data,
            'banners': BannerSerializer(banners, many=True).data,
            'version': VersionSerializer(version).data,
        })


def get_mutual_connections(user, target):
    user_connections = Connection.objects.filter(
        first_user=user,
        accepted=True
    ).values_list('second_user_id', flat=True)
    for c in user_connections:
        print(c)

    # Step 2: Find connections between those users and the `other_user_id`
    mutual_connections = Connection.objects.filter(
        first_user_id__in=user_connections,
        second_user_id=target.id,
        accepted=True
    )

    return mutual_connections


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

        if category == 'request':
            queryset = Connection.objects.filter(second_user=self.get_user(),
                                                 accepted=False)
        elif category == 'my_connections':
            queryset = Connection.objects.filter(first_user=self.get_user(),
                                                 accepted=True)
        else:
            target_id = request.query_params.get('target', None)
            if not target_id:
                return Response({'error': 'target is required'}, status=status.HTTP_400_BAD_REQUEST)
            target = get_object_or_404(CustomUser, id=target_id)
            queryset = Connection.objects.filter(first_user=target,
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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mutual(self, request):
        user = self.get_user()
        target_id = request.query_params.get('target_id', None)
        if not target_id:
            return Response({'error': 'target_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        target = get_object_or_404(CustomUser, id=target_id)

        connections = get_mutual_connections(user, target)
        return Response(ConnectionSerializer(connections, many=True).data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def list(self, request, *args, **kwargs):
        categories = Category.objects.filter(is_active=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def my_categories(self, request):
        user = self.get_user()
        id_list = request.data.get('id_list', None)
        if not id_list:
            return Response({'error': 'id_list is required'}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            for ca in id_list:
                category = get_object_or_404(Category, id=ca)
                user_category = UserCategory(user=user, category=category)
                user_category.save()

            return Response(status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            for ca in id_list:
                user_category = get_object_or_404(UserCategory, user=user, category=ca)
                user_category.delete()

            return Response(status=status.HTTP_200_OK)
