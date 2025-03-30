from django.shortcuts import render

# Create your views here.
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="Home") ,
    path("inventory/", views.inventory_view, name="inventory"),
    path('signup' , views.signup , name = 'signup') ,
    path('login' , views.login , name = 'login') ,
    path('test/' , views.test , name = 'test')
]
