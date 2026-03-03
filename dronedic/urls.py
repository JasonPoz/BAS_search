from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dictionary import views as dictionary_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dictionary.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # <-- это исправляет твою ошибку
    path('users/', include('users.urls', namespace='users')),
    path('registration/', dictionary_views.registration_view, name='registration'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
