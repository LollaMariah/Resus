from django.contrib import admin
from django.urls import path, include
from Resus_App import views  # Importing the views module
from Resus_App.views import SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),  # Using views.home
    path('', views.index, name='index'),  # Using views.index
    path('kursus/', views.kursus_card, name='kursus'),  # Using views.kursus_card # Using views.show_persons
    path('login/', views.login, name='login'),  # Using views.login
    path('registrasi/', views.registrasi, name='registrasi'),  # Using views.registrasi
    path('detail_kursus/', views.detail_kursus, name='detail_kursus'),  # Using views.detail_kursus
    path('role/', views.pilih_role, name='pilih_role'),  # Using views.pilih_role
    path('accounts/', include('registration.backends.default.urls')),
    path('signup/', SignUpView.as_view(), name='signup'),
   
]
