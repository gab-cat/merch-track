from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("trackOrder", views.home, name='trackOrder'),
    path("aboutUs", views.aboutUs, name='aboutUs'),
    path("contactUs", views.home, name='contactUs'),
    path("base", views.base, name='base'),
    path("index", views.index, name='index'),
]