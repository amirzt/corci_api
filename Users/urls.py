from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path
from .views import UsersViewSet

router = DefaultRouter()
router.register(r'', UsersViewSet, basename='user')
urlpatterns = [
    path('', include(router.urls)),
]
