import markdown
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils.safestring import mark_safe
from django.http import HttpRequest, HttpResponse
from django.db.models import Count, Q 
from django.utils import timezone

# Importações dos modelos
from .models import Trail, Chapter, PointTransaction, UserProgress, Alternativa, Questao
from .utils import check_user_medals

logger = logging.getLogger(__name__)

# --- 1. HOME / INDEX ---
def index(request):
    all_trails = Trail.objects.annotate(num_chapters=Count('chapters'))

    if not request.user.is_authenticated:
        return render(request, 'gamification/index.html', {'all_trails': all_trails})

    user = request.user
    started_ids = UserProgress.objects.filter(user=user).values_list('chapter__trail_id', flat=True).distinct()
    my_trails = all_trails.filter(id__in=started_ids)
    suggested_trails = all_trails.exclude(id__in=started_ids)[:4]

    total_sys = Chapter.objects.count()
    total_done = UserProgress.objects.filter(user=user, completed_at__isnull=False).count()
    overall_progress = int((total_done / total_sys) * 100) if total_sys > 0 else 0

    context = {
        'my_trails': my_trails,
        'suggested_trails': suggested_trails,
        'overall_progress': overall_progress,
        'tech_list': ["python", "docker", "js", "database", "git-alt", "cloud"],
    }
    return render(request, 'gamification/home.html', context)

# --- 2. LISTAGENS ---
@login_required
def trail_list(request):
    trails = Trail.objects.all()
    return render(request, 'gamification/trail_list.html', {'trails': trails})

@login_required
def trail_detail(request, trail_id):
    trail = get_object_or_404(Trail, id=trail_id)
    chapters = trail.chapters.all().order_by('order')
    
    completed_ids = UserProgress.objects.filter(
        user=request.user, 
        chapter__trail=trail, 
        completed_at__isnull=False
    ).values_list('chapter_id', flat=True)

    progress = 0
    if chapters.count() > 0:
        progress = (len(completed_ids) / chapters.count()) * 100

    for chapter in chapters:
        chapter.is_completed = chapter.id in completed_ids
        chapter.unlocked = chapter.is_unlocked(request.user)

    return render(request, 'gamification/trail_detail.html', {
        'trail': trail, 'chapters': chapters, 'progress': progress
    })

# --- 3. AULA E LEITURA (20% XP) ---
@login_required
def chapter_detail(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    if not chapter.is_unlocked(request.user):
        messages.error(request, "🛡️ Unidade Bloqueada.")
        return redirect('gamification:trail_detail', trail_id=chapter.trail.id)

    html_output = markdown.markdown(chapter.content or "", extensions=['fenced_code', 'codehilite', 'tables'])
    chapter.content_html = mark_safe(html_output)
    return render(request, 'gamification/chapter_detail.html', {'chapter': chapter})

@login_required
def complete_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    user = request.user
    xp_leitura = int(chapter.xp_value * 0.2)

    ja_ganhou_leitura = PointTransaction.objects.filter(user=user).filter(
        Q(description=f"Leitura: {chapter.title}") | Q(description__icontains=f"Conclusão: {chapter.title}")
    ).exists()

    if not ja_ganhou_leitura:
        with transaction.atomic():
            PointTransaction.objects.create(user=user, quantity=xp_leitura, description=f"Leitura: {chapter.title}")
            user.xp += xp_leitura
            user.save()
            UserProgress.objects.get_or_create(user=user, chapter=chapter)
            messages.success(request, f"🛡️ Checkpoint: +{xp_leitura} XP garantidos!")

    return redirect('gamification:exibir_quiz', slug=chapter.slug)

# --- 4. QUIZ (80% XP) ---
@login_required
def exibir_quiz(request, slug):
    """
    GATILHO 2: Processa o Quiz.
    Libera 80% do XP total e marca a conclusão temporal da aula.
    """
    capitulo = get_object_or_404(Chapter, slug=slug)
    questoes = capitulo.questoes.all().prefetch_related('alternativas')
    user = request.user
    
    # Define o valor do Quiz (80% do total do capítulo)
    xp_quiz = int(capitulo.xp_value * 0.8)

    # Verifica se já recebeu pontos (Método Novo ou Legado)
    ja_ganhou_antes = PointTransaction.objects.filter(user=user).filter(
        Q(description=f"Aprovação Quiz: {capitulo.title}") | 
        Q(description__icontains=f"Conclusão: {capitulo.title}")
    ).exists()
    
    if request.method == "POST":
        acertos = 0
        total = questoes.count()
        detalhes = []

        for q in questoes:
            alt_id = request.POST.get(f'questao_{q.id}')
            escolha = Alternativa.objects.filter(id=alt_id).first() if alt_id else None
            correta = q.alternativas.filter(e_correta=True).first()
            
            is_correct = bool(escolha and escolha.e_correta)
            if is_correct: 
                acertos += 1
            
            detalhes.append({
                'pergunta': q.enunciado,
                'escolha': escolha.texto if escolha else "Não respondida",
                'correta': correta.texto if correta else "N/A",
                'foi_correta': is_correct
            })

        percentual = (acertos / total * 100) if total > 0 else 0
        aprovado = percentual >= 70
        pode_receber_pontos = False

        if aprovado:
            with transaction.atomic():
                # Marca a conclusão real (preenche a barra de sincronia)
                prog, _ = UserProgress.objects.get_or_create(user=user, chapter=capitulo)
                prog.completed_at = timezone.now()
                prog.save()

                if not ja_ganhou_antes:
                    # Registra os 80% de XP
                    PointTransaction.objects.create(
                        user=user, 
                        quantity=xp_quiz, 
                        description=f"Aprovação Quiz: {capitulo.title}"
                    )
                    user.xp += xp_quiz
                    user.save(update_fields=['xp'])
                    
                    # Verifica medalhas
                    check_user_medals(user)
                    pode_receber_pontos = True

        return render(request, 'gamification/quiz_resultado.html', {
            'capitulo': capitulo, 
            'aprovado': aprovado, 
            'percentual': int(percentual),
            'acertos': acertos, 
            'total': total, 
            'resultados': detalhes, 
            'pontos': xp_quiz, # Usado para exibir o valor ganho
            'pode_receber_pontos': pode_receber_pontos,
            'ja_ganhou_pontos': ja_ganhou_antes
        })

    # --- RETORNO PARA O CARREGAMENTO INICIAL (GET) ---
    return render(request, 'gamification/quiz.html', {
        'capitulo': capitulo, 
        'questoes': questoes,
        'ja_fez_quiz': ja_ganhou_antes,
        'xp_remanescente': xp_quiz  # <--- SINCRONIZADO: Agora o template verá o valor!
    })

# --- 5. EXTRAS ---
@login_required
def checkout(request):
    if request.method == "POST":
        request.user.is_plus = True
        request.user.save()
        messages.success(request, "🚀 Assinatura Plus Ativada!")
        return redirect('gamification:trail_list')
    return render(request, 'gamification/checkout.html')

def tech_detail(request, tech_slug):
    trails = Trail.objects.filter(title__icontains=tech_slug)
    return render(request, 'gamification/tech_detail.html', {'tech_name': tech_slug.upper(), 'trails': trails})

def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)

def responder_questao(request, questao_id):
    """ Processa a resposta enviada pelo aluno """
    if request.method == "POST":
        # A lógica de validação entraremos em detalhe no próximo passo
        return redirect('gamification:exibir_quiz', slug="slug-do-capitulo")
    return redirect('gamification:trail_list') # Redirecionamento temporário