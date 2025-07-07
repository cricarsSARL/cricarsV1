"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('car_listing/', views.car_listing, name='car_listing'),
    path('become-host/', views.become_host, name='become_host'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('host_register/', views.host_register, name='host_register'),
    path('host_login/', views.host_login, name='host_login'),
    path('profile/', views.profile, name='profile'),
    path('addcar/', views.addcar, name='addcar'),
    path('logout/', views.logout, name='logout'),
    path('car_list/', views.car_list, name='car_list'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('car/<int:car_id>/book/', views.book_car, name='book_car'),
    path('legal_view/', views.legal_view, name='legal_view'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
