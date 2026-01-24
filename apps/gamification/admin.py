from django.contrib import admin
from .models import Medal, Trail, Chapter, PointTransaction, UserMedal
from .services import gerar_conteudo_aula

# --- ADMIN ACTIONS (Inteligência Artificial) ---

from django.contrib import messages # Importe isso no topo

@admin.action(description="Gerar conteúdo inteligente via IA")
def automatizar_conteudo(modeladmin, request, queryset):
    for chapter in queryset:
        print(f"--- Iniciando IA para: {chapter.title} ---") # LOG DE DEBUG
        conteudo_gerado = gerar_conteudo_aula(chapter.title)
        
        print(f"Conteúdo recebido: {conteudo_gerado[:50]}...") # VERIFICA SE VEIO TEXTO
        
        if conteudo_gerado:
            chapter.content = conteudo_gerado
            chapter.save()
        else:
            print("AVISO: A IA retornou conteúdo vazio!")

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    fields = ('order', 'title', 'xp_value')

# --- REGISTROS DOS MODELOS ---

@admin.register(Trail)
class TrailAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'get_chapter_count', 'image')
    search_fields = ('title',)
    inlines = [ChapterInline]

    def get_chapter_count(self, obj):
        return obj.chapters.count()
    get_chapter_count.short_description = "Nº de Capítulos"

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    # Adicionamos 'video_url' aqui para você conferir o link direto na lista
    list_display = ('title', 'trail', 'video_url', 'xp_value', 'order') 
    list_filter = ('trail',)
    search_fields = ('title', 'content')
    list_editable = ('order', 'xp_value')
    actions = [automatizar_conteudo] 
    
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

@admin.register(Medal)
class MedalAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_points')
    search_fields = ('name',)

@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quantity', 'description', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)

@admin.register(UserMedal)
class UserMedalAdmin(admin.ModelAdmin):
    list_display = ('user', 'medal', 'earned_at')
    list_filter = ('user', 'medal')
    readonly_fields = ('earned_at',)