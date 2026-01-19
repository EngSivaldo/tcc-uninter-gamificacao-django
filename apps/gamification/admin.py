from django.contrib import admin
from .models import Medal, Trail, Chapter, PointTransaction

# 1. Configuração Inline (Sênior): Permite editar capítulos dentro da trilha
class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1 # Mostra um espaço vazio para nova aula por padrão
    fields = ('order', 'title', 'xp_value') # Campos simplificados para o inline

@admin.register(Trail)
class TrailAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'get_chapter_count')
    search_fields = ('title',)
    inlines = [ChapterInline] # Adiciona a gestão de capítulos aqui dentro

    def get_chapter_count(self, obj):
        return obj.chapters.count()
    get_chapter_count.short_description = "Nº de Capítulos"

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'trail', 'xp_value', 'order')
    list_filter = ('trail',)
    search_fields = ('title', 'content')
    list_editable = ('order', 'xp_value') # Permite editar a ordem direto na lista

@admin.register(Medal)
class MedalAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_points')
    search_fields = ('name',)

@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quantity', 'description', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',) # Impede alteração da data de ganho