from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Define quais campos aparecem na lista de usuários
    list_display = ('username', 'email', 'ru', 'xp', 'is_staff')
    
    # Adiciona os novos campos nos formulários de edição
    fieldsets = UserAdmin.fieldsets + (
        ("Informações Acadêmicas e Gamificação", {'fields': ('ru', 'points')}),
    )
    
    # Adiciona os novos campos no formulário de criação
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informações Acadêmicas", {'fields': ('ru', 'points')}),
    )