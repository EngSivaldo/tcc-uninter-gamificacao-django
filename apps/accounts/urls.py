from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

app_name = 'accounts'

urlpatterns = [
    #Área do Estudante (Página Principal após o login)
    # AJUSTADO: Removido o .as_view() e a linha duplicada
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Fluxo de Autenticação (Django Auth System)
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Fluxo de Novos Alunos (Cadastro/Registro)
    path('register/', views.register, name='register'),
]






#1. O Território de Identidade (apps/accounts/urls.py)
# Este arquivo cuida de quem é o usuário:

# register/: Usa o seu formulário customizado com RU para criar novos alunos.

# login/logout/: Gerencia a entrada e saída usando o sistema nativo do Django.