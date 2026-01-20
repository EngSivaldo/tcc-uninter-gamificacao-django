from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trail, Chapter, PointTransaction
from .utils import check_user_medals  # Importante: Importe a função que criamos

@login_required
def trail_list(request):
    """Lista todas as trilhas (ex: Engenharia de Software)."""
    trails = Trail.objects.all()
    return render(request, 'gamification/trail_list.html', {'trails': trails})

@login_required
def trail_detail(request, trail_id):
    """Mostra os capítulos de uma trilha específica."""
    trail = get_object_or_404(Trail, id=trail_id)
    return render(request, 'gamification/trail_detail.html', {'trail': trail})


# apps/gamification/views.py

@login_required
def chapter_detail(request, chapter_id):
    """Exibe o conteúdo de uma única aula."""
    chapter = get_object_or_404(Chapter, id=chapter_id)
    return render(request, 'gamification/chapter_detail.html', {'chapter': chapter})



@login_required
def complete_chapter(request, chapter_id):
    """Lógica que gera os pontos e verifica medalhas automaticamente."""
    chapter = get_object_or_404(Chapter, id=chapter_id)
    
    # Verifica duplicidade para garantir a integridade (RNF01) 
    already_done = PointTransaction.objects.filter(
        user=request.user, 
        description__contains=f"Conclusão: {chapter.title}"
    ).exists()

    if not already_done:
        # 1. Cria a transação de pontos no banco de dados [cite: 37]
        PointTransaction.objects.create(
            user=request.user,
            quantity=chapter.xp_value,
            description=f"Conclusão: {chapter.title}"
        )
        
        # 2. Gatilho de Medalhas: Verifica se o novo saldo liberou conquistas [cite: 38]
        novas_conquistas = check_user_medals(request.user)
        
        if novas_conquistas:
            # Notificação visual de conquista (RF04)
            medalhas_str = ", ".join(novas_conquistas)
            messages.success(request, f"Parabéns! Ganhaste {chapter.xp_value} XP e novas medalhas: {medalhas_str}!")
        else:
            messages.success(request, f"Parabéns! Ganhaste {chapter.xp_value} XP!")
    else:
        messages.warning(request, "Esta aula já foi concluída anteriormente.")

    return redirect('accounts:dashboard')