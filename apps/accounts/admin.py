from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 1. Campos que aparecem na lista de usuários
    list_display = ('username', 'ru', 'xp', 'is_plus', 'is_staff')
    list_filter = ('is_plus', 'is_staff', 'is_superuser')
    
    # 2. Campos que aparecem ao EDITAR um usuário existente
    # Trocamos 'points' por 'xp' aqui
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Acadêmicas', {'fields': ('ru',)}),
        ('Gamificação', {'fields': ('xp', 'is_plus')}),
    )
    
    # 3. Campos que aparecem ao ADICIONAR um novo usuário (Onde dava o erro)
    # Trocamos 'points' por 'xp' aqui também
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Acadêmicas', {'fields': ('ru', 'xp', 'is_plus')}),
    )

    # Ordenação padrão no admin
    ordering = ('-date_joined',)