from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils.safestring import mark_safe
from django.http import HttpRequest, HttpResponse
import markdown
import logging

# Importações dos modelos do seu domínio
from .models import Trail, Chapter, PointTransaction, UserProgress
from .utils import check_user_medals

# Configuração de Logs para monitorar erros de produção
logger = logging.getLogger(__name__)

@login_required
def trail_list(request: HttpRequest) -> HttpResponse:
    """Lista todas as trilhas disponíveis no catálogo."""
    trails = Trail.objects.all()
    return render(request, 'gamification/trail_list.html', {'trails': trails})

@login_required
def trail_detail(request: HttpRequest, trail_id: int) -> HttpResponse:
    """
    Exibe os capítulos de uma trilha com cálculo de progresso matemático.
    A fórmula utilizada para o progresso é:
    $$P = \left( \frac{C_{comp}}{C_{total}} \right) \times 100$$
    """
    trail = get_object_or_404(Trail, id=trail_id)
    chapters = trail.chapters.all()
    
    total_chapters = chapters.count()
    completed_chapters = UserProgress.objects.filter(
        user=request.user, 
        chapter__trail=trail
    ).count()
    
    progress_percentage = (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0
    
    context = {
        'trail': trail,
        'chapters': chapters,
        'progress': progress_percentage,
        'completed_count': completed_chapters,
        'total_count': total_chapters,
    }
    return render(request, 'gamification/trail_detail.html', context)

@login_required
def chapter_detail(request: HttpRequest, chapter_id: int) -> HttpResponse:
    """
    Exibe o conteúdo da aula com Trava de Segurança Premium e renderização Markdown.
    A trava de segurança garante que conteúdos Premium não sejam acessados sem 'is_plus'.
    """
    chapter = get_object_or_404(Chapter, id=chapter_id)
    
    # --- CAMADA DE SEGURANÇA BACKEND ---
    if chapter.is_premium and not request.user.is_plus:
        messages.info(request, "🛡️ Conteúdo Exclusivo: Esta aula está disponível apenas no Plano Plus.")
        return redirect('gamification:checkout') 
    
    raw_content = chapter.content or ""
    try:
        html_output = markdown.markdown(
            raw_content, 
            extensions=['fenced_code', 'codehilite', 'tables', 'toc']
        )
        chapter.content_html = mark_safe(html_output)
    except Exception as e:
        logger.error(f"Erro na renderização do Markdown para o capítulo {chapter_id}: {e}")
        chapter.content_html = mark_safe("<p class='text-red-500'>Erro ao carregar conteúdo técnico.</p>")

    return render(request, 'gamification/chapter_detail.html', {'chapter': chapter})

@login_required
def complete_chapter(request: HttpRequest, chapter_id: int) -> HttpResponse:
    """
    Conclui a aula, registra progresso e concede XP usando transação atômica.
    """
    
    chapter = get_object_or_404(Chapter, id=chapter_id)
    user = request.user

    already_done = PointTransaction.objects.filter(
        user=user,
        description=f"Conclusão: {chapter.title}"
    ).exists()

    if already_done:
        messages.warning(request, "Você já concluiu esta etapa e recebeu seu XP.")
        return redirect('gamification:trail_detail', trail_id=chapter.trail.id)

    try:
        with transaction.atomic():
            UserProgress.objects.get_or_create(user=user, chapter=chapter)
            PointTransaction.objects.create(
                user=user,
                quantity=chapter.xp_value,
                description=f"Conclusão: {chapter.title}"
            )
            user.xp += chapter.xp_value
            user.save(update_fields=["xp"])
            novas_conquistas = check_user_medals(user)

        if novas_conquistas:
            messages.success(request, f"🏆 Impressionante! +{chapter.xp_value} XP e novas medalhas: {', '.join(novas_conquistas)}!")
        else:
            messages.success(request, f"✅ Aula finalizada! +{chapter.xp_value} XP adicionado.")

    except Exception as e:
        logger.error(f"Erro crítico na gamificação (User {user.id}): {e}")
        messages.error(request, "Erro ao processar recompensa.")

    return redirect('gamification:trail_detail', trail_id=chapter.trail.id)

@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    """
    Processa a simulação de pagamento. 
    Ao clicar em confirmar, o status 'is_plus' do usuário é ativado.
    """
    if request.method == "POST":
        user = request.user
        # Lógica de ativação
        user.is_plus = True
        user.save(update_fields=["is_plus"])
        
        messages.success(request, "🚀 Assinatura Plus Ativada! Todos os conteúdos premium foram liberados.")
        return redirect('gamification:trail_list') # Redireciona para o catálogo
        
    return render(request, 'gamification/checkout.html')
def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)