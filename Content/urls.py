from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path
from .views import ContentViewSet, ResponsibleViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'content', ContentViewSet, basename='content')
router.register(r'responsible', ResponsibleViewSet, basename='responsible')
router.register(r'comment', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]
