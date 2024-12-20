from rest_framework.routers import DefaultRouter
from .views import ChatViewSet

router = DefaultRouter()
router.register(r'', ChatViewSet, basename='')

urlpatterns = router.urls
