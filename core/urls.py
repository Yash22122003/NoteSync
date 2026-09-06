from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('notes/', include('notes.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/', include('notes.api_urls')),
]