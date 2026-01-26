from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils.safestring import mark_safe
from django.http import HttpRequest, HttpResponse
import markdown
import logging
from django.utils import timezone


# Importações dos modelos do seu domínio
from .models import Trail, Chapter, PointTransaction, UserProgress
from .utils import check_user_medals

# Configuração de Logs para monitorar erros de produção

def index(request):
    # Buscamos as trilhas com contagem de capítulos em UMA única consulta (Performance Sênior)
    from django.db.models import Count
    all_trails = Trail.objects.annotate(num_chapters=Count('chapters'))

    if not request.user.is_authenticated:
        return render(request, 'gamification/index.html', {'all_trails': all_trails})

    user = request.user
    
    # select_related evita idas extras ao banco
    last_progress = UserProgress.objects.filter(user=user)\
        .select_related('chapter__trail')\
        .order_by('-updated_at').first()
    
    current_trail_progress = 0
    if last_progress:
        trail = last_progress.chapter.trail
        total_ch = trail.chapters.count()
        done_ch = UserProgress.objects.filter(user=user, chapter__trail=trail).count()
        current_trail_progress = int((done_ch / total_ch) * 100) if total_ch > 0 else 0

    # Progresso Global
    total_sys = Chapter.objects.count()
    total_done = UserProgress.objects.filter(user=user).count()
    overall_progress = int((total_done / total_sys) * 100) if total_sys > 0 else 0

    # Sugestões: Excluímos o que ele já começou
    started_ids = UserProgress.objects.filter(user=user).values_list('chapter__trail_id', flat=True).distinct()
    suggested_trails = all_trails.exclude(id__in=started_ids)[:4]

    context = {
        'last_progress': last_progress,
        'current_trail_progress': current_trail_progress, 
        'overall_progress': overall_progress,           
        'suggested_trails': suggested_trails,
        'all_trails': all_trails,
    }
    return render(request, 'gamification/home.html', context)

@login_required
def trail_list(request: HttpRequest) -> HttpResponse:
    """Lista todas as trilhas disponíveis no catálogo."""
    trails = Trail.objects.all()
    return render(request, 'gamification/trail_list.html', {'trails': trails})

def trail_detail(request, trail_id):
    trail = get_object_or_404(Trail, id=trail_id)
    # Ordenação explícita para evitar confusão na lista
    chapters = trail.chapters.all().order_by('id')
    
    progress = 0
    if request.user.is_authenticated:
        completed = UserProgress.objects.filter(user=request.user, chapter__trail=trail).count()
        if chapters.count() > 0:
            progress = (completed / chapters.count()) * 100

    context = {
        'trail': trail,
        'chapters': chapters,
        'progress': progress,
        'total_count': chapters.count(),
        'price': "119,90", 
        'old_price': "497,00"
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