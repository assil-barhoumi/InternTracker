"""
URL configuration for config project.

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
from core import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),  
    path('login/', auth_views.LoginView.as_view(next_page='offer_list'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path("offers/", views.offer_list, name="offer_list"),
    path('offers/apply/<int:offer_id>/', views.apply_offer, name='apply_offer'),
    path('profile/upload-cv/', login_required(views.upload_cv), name='upload_cv'),
   
]
