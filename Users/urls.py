from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path
from .views import UsersViewSet, ConnectionViewSet

router = DefaultRouter()
router.register(r'', UsersViewSet, basename='user')
router.register(r'connection', ConnectionViewSet, basename='connection')

urlpatterns = [
    path('', include(router.urls)),
]
