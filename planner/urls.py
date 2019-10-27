from django.urls import path
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views, save

urlpatterns = [
    url('', views.index, name='index'),
]
