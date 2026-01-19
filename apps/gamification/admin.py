from django.contrib import admin
from .models import Medal, PointTransaction

@admin.register(Medal)
class MedalAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_points')

@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quantity', 'description', 'created_at')
    list_filter = ('user', 'created_at')
    
    
    
#Para que você e a Eralice possam cadastrar medalhas manualmente pelo painel azul, configure o arquivo apps/gamification/admin.py: