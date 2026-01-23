from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    # Rotas de Navegação de Conteúdo
    path('trilhas/', views.trail_list, name='trail_list'),
    path('trilha/<int:trail_id>/', views.trail_detail, name='trail_detail'),
    path('capitulo/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    
    # Rota de Lógica de Gamificação (Ação de Concluir Aula)
    path('concluir/<int:chapter_id>/', views.complete_chapter, name='complete_chapter'),
    
    # Rota de Conversão e Vendas (Pilar da Monetização)
    path('checkout/', views.checkout, name='checkout'),
]