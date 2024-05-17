from django.conf import settings
from django.views.static import serve
from django.urls import path,re_path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("trackOrder", views.trackOrder, name='trackOrder'),
    path("aboutUs", views.aboutUs, name='aboutUs'),
    path("contactUs", views.contactUs, name='contactUs'),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    re_path(r'^.*$', views.not_found, name='404'),
]