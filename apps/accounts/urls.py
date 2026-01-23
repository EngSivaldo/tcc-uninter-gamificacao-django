from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

app_name = 'accounts'

urlpatterns = [
    # Área Administrativa do Aluno
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Fluxo de Autenticação (Django Auth System)
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Fluxo de Novos Alunos (Conversão)
    path('register/', views.register, name='register'),
]