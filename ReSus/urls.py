from django.contrib import admin
from django.urls import path
from ReSus.views import kursus_card
from ReSus.views import login
from ReSus.views import registrasi
from ReSus.views import detail_kursus
from ReSus.views import show_persons
from ReSus.views import pilih_role

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('', views.index, name='index'),
    path('kursus/', kursus_card, name='kursus'),
    path('show_gds/', show_persons, name='show_persons'),
    path('login/', login, name='login'), 
    path('registrasi/', registrasi, name='registrasi'), 
    path('detail_kursus/', detail_kursus, name='detail_kursus'), 
    path('role/', pilih_role, name='pilih_role'), 
]
