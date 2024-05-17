from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("trackOrder", views.trackOrder, name='trackOrder'),
    path("aboutUs", views.aboutUs, name='aboutUs'),
    path("contactUs", views.contactUs, name='contactUs'),
]