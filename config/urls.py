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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/applications/', views.admin_application_list, name='admin_application_list'),
    path('admin/interviews/', views.admin_interviews_list, name='admin_interviews_list'),
    path('admin/offers/', views.admin_offers_list, name='admin_offers_list'),
    path('admin/interns/', views.admin_interns_list, name='admin_interns_list'),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),  
    path('login/', auth_views.LoginView.as_view(next_page='offer_list'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path("offers/", views.offer_list, name="offer_list"),
    path('offers/apply/<int:offer_id>/', views.apply_offer, name='apply_offer'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', login_required(views.edit_profile), name='edit_profile'),
    path('profile/upload-cv/', login_required(views.upload_cv), name='upload_cv'),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)