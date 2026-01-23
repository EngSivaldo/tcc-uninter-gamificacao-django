# Arquivo: apps/accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views # Importamos as views do seu app
from .views import DashboardView

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # NOVA ROTA: Agora o erro 'register not found' vai desaparecer
    path('register/', views.register, name='register'),
]