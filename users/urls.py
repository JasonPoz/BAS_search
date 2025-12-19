from django.urls import include, path

from . import views

app_name = 'users'

profile_urls = [
    path('edit/', views.edit_profile, name='edit_profile'),
    path('<slug:username>/', views.profile, name='profile'),
    ]

urlpatterns = [
    path('profile/', include(profile_urls)),
]