from django.urls import path
from . import views

urlpatterns = [
    path('',          views.index,     name='index'),
    path('customize/', views.customize, name='customize'),
]