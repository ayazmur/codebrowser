from django.urls import path
from . import views

app_name = 'browser'

urlpatterns = [
    path('', views.index, name='index'),
    path('proxy', views.proxy, name='proxy'),
]
