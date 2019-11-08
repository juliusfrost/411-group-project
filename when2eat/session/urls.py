from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('join/', views.join, name='join'),
    path('join/<int:session_id>', views.join_session, name='join'),
]
