from django.urls import path,re_path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("trackOrder", views.home, name='trackOrder'),
    path("aboutUs", views.home, name='aboutUs'),
    path("contactUs", views.home, name='contactUs'),
    re_path(r'^.*$', views.not_found, name='404'),
]