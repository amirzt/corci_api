from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path
from .views import UserNotificationViewSet

router = DefaultRouter()
router.register(r'', UserNotificationViewSet, basename='')

urlpatterns = [
    path('', include(router.urls)),
]
