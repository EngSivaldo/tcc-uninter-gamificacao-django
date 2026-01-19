from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trail, Chapter, PointTransaction

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
    """Lógica que gera os pontos automaticamente."""
    chapter = get_object_or_404(Chapter, id=chapter_id)
    
    # Verifica se o aluno já ganhou pontos por esta aula (Segurança Sênior)
    already_done = PointTransaction.objects.filter(
        user=request.user, 
        description__contains=f"Conclusão: {chapter.title}"
    ).exists()

    if not already_done:
        # Cria a transação de pontos automática no banco de dados
        PointTransaction.objects.create(
            user=request.user,
            quantity=chapter.xp_value,
            description=f"Conclusão: {chapter.title}"
        )
        messages.success(request, f"Parabéns! Ganhaste {chapter.xp_value} XP!")
    else:
        messages.warning(request, "Esta aula já foi concluída anteriormente.")

    return redirect('accounts:dashboard')