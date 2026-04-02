from django.urls import path
from . import views

urlpatterns = [
    path('',          views.index,     name='index'),
    path('customize/', views.customize, name='customize'),
    path('api/update-theme/', views.update_settings_api, name='api_update_theme'),
]