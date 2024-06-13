from django.contrib import admin
from django.urls import path, include
from Resus_App import views  # Mengimpor modul views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('role/', views.pilih_role, name='pilih_role'),
    path('topics/', views.topics, name='topics'),
    path('accounts/', include('registration.backends.default.urls')),
    path('Resus_App/', include('Resus_App.urls')),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('access_course/<str:course_id>/', views.access_course, name='access_course'),
    path('topics_recommend/', views.all_topics, name='all_topics'),
    path('role_recommend/', views.all_role, name='all_role'),
    path('courses/recommended/', views.recommended_courses, name='recommended_courses'),
    path('profile/', views.accessed_users, name='accessed_users'),
    path('access_course/', views.access_course, name='access_course'),
]
