from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('trilhas/', views.trail_list, name='trail_list'),
    path('trilha/<int:trail_id>/', views.trail_detail, name='trail_detail'),
    # NOVA ROTA:
    path('capitulo/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    path('concluir/<int:chapter_id>/', views.complete_chapter, name='complete_chapter'),
    
    path('concluir/<int:chapter_id>/', views.complete_chapter, name='complete_chapter'),
    path('checkout/', views.checkout, name='checkout'),
]