import os
import json
from django.contrib import admin, messages
from google import genai
from .models import Medal, Trail, Chapter, Alternativa, PointTransaction, UserMedal, Questao
from .services import gerar_conteudo_aula
import re
import time



# --- ADMIN ACTIONS (Inteligência Artificial) ---

@admin.action(description="🤖 1. Gerar Texto da Aula via IA")
def automatizar_conteudo(modeladmin, request, queryset):
    """Gera o conteúdo em HTML para as aulas selecionadas"""
    for chapter in queryset:
        conteudo_gerado = gerar_conteudo_aula(chapter.title)
        if conteudo_gerado:
            chapter.content = conteudo_gerado
            chapter.save()
            messages.success(request, f"Conteúdo gerado para: {chapter.title}")
        else:
            messages.warning(request, f"A IA falhou em gerar conteúdo para: {chapter.title}")



@admin.action(description="📝 2. Gerar Questionário via IA (Resiliente)")
def gerar_questoes_ia_action(modeladmin, request, queryset):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    sucesso_count = 0
    # Sua lista de modelos testada e aprovada
    modelos_tentar = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']

    for chapter in queryset:
        if not chapter.content:
            messages.warning(request, f"Pulei '{chapter.title}': Não há conteúdo para basear as perguntas.")
            continue

        # Prompt estruturado para garantir que a IA entenda o formato de dados
        prompt = f"""
        OBJETIVO: Gerar 3 questões de múltipla escolha sobre: "{chapter.content}"
        RETORNE APENAS UM JSON PURO (ARRAY):
        [
          {{
            "enunciado": "Pergunta?",
            "xp": 10,
            "alternativas": [
              {{"texto": "Opção A", "correta": true}},
              {{"texto": "Opção B", "correta": false}},
              {{"texto": "Opção C", "correta": false}},
              {{"texto": "Opção D", "correta": false}}
            ]
          }}
        ]
        """
        
        gerou_para_este_capitulo = False
        
        for modelo in modelos_tentar:
            try:
                # Chamada da API
                response = client.models.generate_content(
                    model=modelo,
                    contents=prompt
                )
                
                if response and response.text:
                    # --- SANITIZAÇÃO (Igual ao que você usa no texto da aula) ---
                    # Remove ```json, ``` e a própria palavra json que podem vir na resposta
                    texto_limpo = re.sub(r'```json|```|json', '', response.text).strip()
                    
                    questoes_data = json.loads(texto_limpo)
                    
                    for item in questoes_data:
                        q = Questao.objects.create(
                            chapter=chapter,
                            enunciado=item['enunciado'],
                            xp_recompensa=item.get('xp', 10)
                        )
                        for alt in item['alternativas']:
                            Alternativa.objects.create(
                                questao=q,
                                texto=alt['texto'],
                                e_correta=alt['correta']
                            )
                    
                    gerou_para_este_capitulo = True
                    sucesso_count += 1
                    break  # Conseguiu! Sai do loop de modelos e vai para o próximo capítulo
                
            except Exception as e:
                erro_msg = str(e)
                if "429" in erro_msg or "RESOURCE_EXHAUSTED" in erro_msg:
                    # Se for erro de cota, espera um pouco e tenta o próximo modelo
                    time.sleep(2)
                    continue 
                else:
                    messages.error(request, f"Erro no modelo {modelo} (Capítulo {chapter.title}): {erro_msg}")
                    # Em caso de erro desconhecido, tentamos o próximo modelo também
                    continue

    if sucesso_count > 0:
        messages.success(request, f"✅ Sucesso! Questões geradas para {sucesso_count} capítulos.")
    else:
        messages.error(request, "❌ A IA não conseguiu gerar as questões. Verifique os logs ou a cota da API.")

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    fields = ('order', 'title', 'xp_value')

class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 4
    min_num = 2
    max_num = 10

# --- REGISTROS ---

@admin.register(Trail)
class TrailAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'get_chapter_count')
    search_fields = ('title',)
    inlines = [ChapterInline]

    def get_chapter_count(self, obj):
        return obj.chapters.count()
    get_chapter_count.short_description = "Nº de Capítulos"

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'trail', 'order', 'xp_value')
    list_filter = ('trail',)
    search_fields = ('title', 'content')
    list_editable = ('order', 'xp_value')
    # AQUI ESTÃO AS DUAS AÇÕES INTEGRADAS:
    actions = [automatizar_conteudo, gerar_questoes_ia_action] 

@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ('enunciado_curto', 'chapter', 'xp_recompensa', 'created_at')
    list_filter = ('chapter', 'created_at')
    search_fields = ('enunciado',)
    inlines = [AlternativaInline]

    def enunciado_curto(self, obj):
        return obj.enunciado[:50] + "..." if len(obj.enunciado) > 50 else obj.enunciado
    enunciado_curto.short_description = "Pergunta"

@admin.register(Alternativa)
class AlternativaAdmin(admin.ModelAdmin):
    list_display = ('texto', 'questao', 'e_correta')
    list_filter = ('e_correta', 'questao')

@admin.register(Medal)
class MedalAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_points')

@admin.register(PointTransaction) # Ajuste o nome se for PointTransaction
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quantity', 'description', 'created_at')

@admin.register(UserMedal)
class UserMedalAdmin(admin.ModelAdmin):
    list_display = ('user', 'medal', 'earned_at')