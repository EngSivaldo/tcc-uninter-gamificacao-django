from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    # --- ROTA RAIZ (PONTO DE ENTRADA INTELIGENTE) ---
    # É aqui que o Django decide: Aluno Logado (Home) vs Visitante (Index)
    path('', views.index, name='index'), 

    # Rotas de Navegação de Conteúdo
    path('trilhas/', views.trail_list, name='trail_list'),
    path('trilha/<int:trail_id>/', views.trail_detail, name='trail_detail'),
    path('capitulo/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    
    # Rota de Lógica de Gamificação (Ação de Concluir Aula)
    path('concluir/<int:chapter_id>/', views.complete_chapter, name='complete_chapter'),
    
    # Rota de Conversão e Vendas (Pilar da Monetização)
    path('checkout/', views.checkout, name='checkout'),
    path('tecnologia/<str:tech_slug>/', views.tech_detail, name='tech_detail'),
    # Rota para exibir o quiz de um capítulo específico
    path('capitulo/<slug:slug>/quiz/', views.exibir_quiz, name='exibir_quiz'),
    
    # Rota para processar a resposta via POST
    path('responder/<int:questao_id>/', views.responder_questao, name='responder_questao'),
]






# 2. O Território de Conteúdo (apps/gamification/urls.py)
# O arquivo que você mostrou anteriormente cuida do que o usuário faz:

# path('', ...): A porta de entrada inteligente que decide se mostra a propaganda (Landing Page) ou o catálogo de cursos (Hub/Home).

# trilhas/, capitulo/: A navegação pelas aulas e conteúdos técnicos.