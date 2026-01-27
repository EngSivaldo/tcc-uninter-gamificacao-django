from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils.safestring import mark_safe
from django.http import HttpRequest, HttpResponse
import markdown
import logging
from django.utils import timezone
from django.db.models import Count


# Importações dos modelos do seu domínio
from .models import Trail, Chapter, PointTransaction, UserProgress
from .utils import check_user_medals



# Defina o logger aqui
logger = logging.getLogger(__name__)

# Configuração de Logs para monitorar erros de produção


# ✅ RESOLVE O ERRO: Define o logger para evitar falhas silenciosas
logger = logging.getLogger(__name__)

def index(request):
    from django.db.models import Count
    all_trails = Trail.objects.annotate(num_chapters=Count('chapters'))

    # --- PORTA DE ENTRADA 1: VISITANTE ---
    if not request.user.is_authenticated:
        return render(request, 'gamification/index.html', {'all_trails': all_trails})

    # --- PORTA DE ENTRADA 2: ALUNO LOGADO ---
    user = request.user
    
    # 1. Filtramos o que ele já começou (Seus Cursos)
    started_ids = UserProgress.objects.filter(user=user).values_list('chapter__trail_id', flat=True).distinct()
    my_trails = all_trails.filter(id__in=started_ids)
    
    # 2. Filtramos o que ele NÃO começou (Sugestões em Cards)
    suggested_trails = all_trails.exclude(id__in=started_ids)[:4]

    # 3. Lógica de Progresso (Sua lógica original preservada)
    last_progress = UserProgress.objects.filter(user=user)\
        .select_related('chapter__trail')\
        .order_by('-updated_at').first()
    
    current_trail_progress = 0
    if last_progress:
        trail = last_progress.chapter.trail
        total_ch = trail.chapters.count()
        done_ch = UserProgress.objects.filter(user=user, chapter__trail=trail).count()
        current_trail_progress = int((done_ch / total_ch) * 100) if total_ch > 0 else 0

    total_sys = Chapter.objects.count()
    total_done = UserProgress.objects.filter(user=user).count()
    overall_progress = int((total_done / total_sys) * 100) if total_sys > 0 else 0

    # 4. Lista para o Arsenal (Evita o erro 'Invalid filter: split')
    tech_list = ["python", "docker", "js", "database", "git-alt", "cloud"]

    context = {
        'my_trails': my_trails,           # O que ele já usa
        'suggested_trails': suggested_trails, # Sugestões (cards com imagem)
        'tech_list': tech_list,           # Lista para o slider
        'last_progress': last_progress,
        'current_trail_progress': current_trail_progress, 
        'overall_progress': overall_progress,
    }
    return render(request, 'gamification/home.html', context)

@login_required
def trail_list(request: HttpRequest) -> HttpResponse:
    """Lista todas as trilhas disponíveis no catálogo."""
    trails = Trail.objects.all()
    return render(request, 'gamification/trail_list.html', {'trails': trails})

def trail_detail(request, trail_id):
    trail = get_object_or_404(Trail, id=trail_id)
    
    # ✅ IMPORTANTE: Usamos 'order' em vez de 'id' para respeitar a sequência didática
    chapters = trail.chapters.all().order_by('order')
    
    progress = 0
    completed_ids = []

    if request.user.is_authenticated:
        # Buscamos apenas os IDs das aulas concluídas para otimizar a performance
        completed_ids = UserProgress.objects.filter(
            user=request.user, 
            chapter__trail=trail
        ).values_list('chapter_id', flat=True)

        total_chapters = chapters.count()
        if total_chapters > 0:
            # Cálculo do progresso usando LaTeX para documentação:
            # $$Progress = \frac{Completed}{Total} \times 100$$
            progress = (len(completed_ids) / total_chapters) * 100

    # ✅ MAPEAMENTO DE ESTADO: 
    # Injetamos as flags 'is_completed' e 'is_unlocked' em cada objeto antes de enviar ao template
    for chapter in chapters:
        chapter.is_completed = chapter.id in completed_ids
        # Chamamos o método que criamos no Model para checar a trava
        chapter.unlocked = chapter.is_unlocked(request.user)

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
    Exibe a aula unindo:
    1. Bloqueio de Sequência (Didática)
    2. Trava Premium (Monetização)
    3. Renderização Markdown (Conteúdo)
    """
    chapter = get_object_or_404(Chapter, id=chapter_id)
    user = request.user
    
    # --- 1. CAMADA DE SEGURANÇA: SEQUÊNCIA (DIDÁTICA) ---
    # Verifica se a aula anterior foi concluída (método que criamos no Model)
    if not chapter.is_unlocked(user):
        messages.error(request, "🛡️ Acesso Negado: Você precisa concluir a unidade anterior para liberar esta aula.")
        return redirect('gamification:trail_detail', trail_id=chapter.trail.id)

    # --- 2. CAMADA DE SEGURANÇA: PREMIUM (MONETIZAÇÃO) ---
    if chapter.is_premium and not user.is_plus:
        messages.info(request, "💎 Conteúdo Exclusivo: Esta aula está disponível apenas no Plano Plus.")
        return redirect('gamification:checkout') 
    
    # --- 3. PROCESSAMENTO DE CONTEÚDO TÉCNICO ---
    raw_content = chapter.content or ""
    try:
        # Renderiza o Markdown com suporte a código e tabelas
        html_output = markdown.markdown(
            raw_content, 
            extensions=['fenced_code', 'codehilite', 'tables', 'toc']
        )
        chapter.content_html = mark_safe(html_output)
    except Exception as e:
        logger.error(f"Erro na renderização do Markdown para o capítulo {chapter_id}: {e}")
        chapter.content_html = mark_safe("<p class='text-red-500 italic'>O subsistema de renderização falhou ao carregar o conteúdo técnico.</p>")

    return render(request, 'gamification/chapter_detail.html', {'chapter': chapter})

@login_required
def complete_chapter(request: HttpRequest, chapter_id: int) -> HttpResponse:
    """
    Conclui a aula, registra progresso, concede XP e navega para a próxima aula.
    Mantém o histórico em PointTransaction e checa medalhas.
    """
    chapter = get_object_or_404(Chapter, id=chapter_id)
    user = request.user

    # ✅ 1. Verificação de Integridade (Usando UserProgress que é mais direto)
    already_done = UserProgress.objects.filter(user=user, chapter=chapter).exists()

    if already_done:
        messages.warning(request, "Você já concluiu esta etapa.")
        # Se já concluiu, vamos tentar mandar ele para a próxima aula mesmo assim
    else:
        try:
            with transaction.atomic():
                # Registra o progresso físico
                UserProgress.objects.get_or_create(user=user, chapter=chapter)
                
                # Registra a transação de pontos (Auditoria)
                PointTransaction.objects.create(
                    user=user,
                    quantity=chapter.xp_value,
                    description=f"Conclusão: {chapter.title}"
                )
                
                # Atualiza o saldo do usuário
                user.xp += chapter.xp_value
                user.save(update_fields=["xp"])
                
                # Checa se o novo XP liberou medalhas
                novas_conquistas = check_user_medals(user)

            if novas_conquistas:
                messages.success(request, f"🏆 Impressionante! +{chapter.xp_value} XP e novas medalhas: {', '.join(novas_conquistas)}!")
            else:
                messages.success(request, f"✅ Unidade finalizada! +{chapter.xp_value} XP adicionado.")

        except Exception as e:
            logger.error(f"Erro crítico na gamificação (User {user.id}): {e}")
            messages.error(request, "Erro ao processar recompensa.")
            return redirect('gamification:trail_detail', trail_id=chapter.trail.id)

    # ✅ 2. LÓGICA DE NAVEGAÇÃO INTELIGENTE (O "Pulo do Gato")
    # Buscamos o próximo capítulo da mesma trilha baseado na ordem
    next_chapter = Chapter.objects.filter(
        trail=chapter.trail, 
        order__gt=chapter.order  # 'order' deve ser um campo no seu model Chapter
    ).order_by('order').first()

    if next_chapter:
        # Se existir próxima aula, vai direto para ela (UX de Elite)
        return redirect('gamification:chapter_detail', chapter_id=next_chapter.id)
    
    # Se for a última aula, volta para a página da trilha para ele ver o 100%
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


# apps/gamification/views.py
def tech_detail(request, tech_slug):
    """View para filtrar trilhas por tecnologia"""
    from .models import Trail
    trails = Trail.objects.filter(title__icontains=tech_slug)
    return render(request, 'gamification/tech_detail.html', {
        'tech_name': tech_slug.upper(),
        'trails': trails
    })