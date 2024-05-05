from django.contrib import admin
from django.urls import path
from ReSus.views import kursus_card
from ReSus.views import login
from ReSus.views import registrasi
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('', views.index, name='index'),
    path('kursus/', kursus_card, name='kursus'),
    path('login/', login, name='login'), 
    path('registrasi/', registrasi, name='registrasi'), 
]
