from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path
from .views import ContentViewSet

router = DefaultRouter()
router.register(r'', ContentViewSet, basename='content')

urlpatterns = [
    path('', include(router.urls)),
]
