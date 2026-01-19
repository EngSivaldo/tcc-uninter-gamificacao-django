from django.urls import path
from django.contrib.auth import views as auth_views
from .views import DashboardView

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]