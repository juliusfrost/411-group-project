from django.urls import path
from . import views

urlpatterns = [
    path('', views.yelpform, name='yelpform'),
    path('yelpsearch', views.yelpsearch, name='yelpsearch'),
]
