
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('Users.urls')),
    path('api/v1/content/', include('Content.urls')),
    path('api/v1/chat/', include('chat.urls')),
    path('api/v1/notification/', include('notification.urls')),

]
