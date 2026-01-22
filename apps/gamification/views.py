from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction # Importante para integridade de dados
from .models import Trail, Chapter, PointTransaction
from .utils import check_user_medals

@login_required
def trail_list(request):
    """Lista todas as trilhas disponíveis."""
    trails = Trail.objects.all()
    return render(request, 'gamification/trail_list.html', {'trails': trails})

@login_required
def trail_detail(request, trail_id):
    """Exibe os capítulos de uma trilha específica."""
    trail = get_object_or_404(Trail, id=trail_id)
    return render(request, 'gamification/trail_detail.html', {'trail': trail})

@login_required
def chapter_detail(request, chapter_id):
    """Exibe o conteúdo da aula."""
    chapter = get_object_or_404(Chapter, id=chapter_id)
    return render(request, 'gamification/chapter_detail.html', {'chapter': chapter})

@login_required
def complete_chapter(request, chapter_id):
    """
    Lógica sênior: Usamos transaction.atomic para garantir que 
    se o XP for salvo, a medalha também seja, ou nada seja feito.
    """
    chapter = get_object_or_404(Chapter, id=chapter_id)
    user = request.user
    
    # 1. Verificação de Integridade
    already_done = PointTransaction.objects.filter(
        user=user, 
        description__icontains=f"Conclusão: {chapter.title}"
    ).exists()

    if not already_done:
        try:
            # 2. Início da Transação Atômica (Garante consistência total)
            with transaction.atomic():
                # Registra transação de pontos
                PointTransaction.objects.create(
                    user=user,
                    quantity=chapter.xp_value,
                    description=f"Conclusão: {chapter.title}"
                )
                
                # Sincroniza o XP no Perfil do Usuário
                user.xp += chapter.xp_value
                user.save()
                
                # 3. Verifica Medalhas (Gatilho do RF04)
                novas_conquistas = check_user_medals(user)
                
                # 4. Feedback ao Usuário
                if novas_conquistas:
                    medalhas_str = ", ".join(novas_conquistas)
                    messages.success(request, f"🏆 Incrível! +{chapter.xp_value} XP e novas medalhas: {medalhas_str}!")
                else:
                    messages.success(request, f"✅ Aula concluída! Você ganhou {chapter.xp_value} XP.")
        
        except Exception as e:
            messages.error(request, "Ocorreu um erro ao processar sua recompensa. Tente novamente.")
            print(f"Erro técnico: {e}")
            
    else:
        messages.warning(request, "Você já recebeu XP por esta aula anteriormente.")

    # Ajuste no redirect: usamos o ID da trilha associada ao capítulo
    return redirect('gamification:trail_detail', trail_id=chapter.trail.id)