from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path
from .views import ContentViewSet, CommentViewSet, OfferViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'content', ContentViewSet, basename='content')
router.register(r'comment', CommentViewSet, basename='comment')
router.register(r'offer', OfferViewSet, basename='offer')
router.register(r'task', TaskViewSet, basename='task')


urlpatterns = [
    path('', include(router.urls)),
]
