from django.urls import path
from . import views

urlpatterns = [
    path('', views.start, name='start'),
    # path('hostSession', views.hostSession, name='hostSession'),
    # path('joinSession', views.joinSession, name='joinSession'),
]
