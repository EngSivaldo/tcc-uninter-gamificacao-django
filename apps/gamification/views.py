import markdown
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils.safestring import mark_safe
from django.http import HttpRequest, HttpResponse
from django.db.models import Count
from django.utils import timezone  # Adicionado para registrar a data de conclusão

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

    # Progresso Geral (AJUSTADO: completed_at__isnull=False)
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
    
    progress = 0
    # AJUSTADO: Filtra quem tem data de conclusão preenchida
    completed_ids = UserProgress.objects.filter(
        user=request.user, 
        chapter__trail=trail, 
        completed_at__isnull=False
    ).values_list('chapter_id', flat=True)

    if chapters.count() > 0:
        progress = (len(completed_ids) / chapters.count()) * 100

    for chapter in chapters:
        chapter.is_completed = chapter.id in completed_ids
        chapter.unlocked = chapter.is_unlocked(request.user)

    return render(request, 'gamification/trail_detail.html', {
        'trail': trail, 'chapters': chapters, 'progress': progress
    })

# --- 3. AULA E LEITURA (50% XP) ---
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
    xp_leitura = int(chapter.xp_value * 0.5)
    ja_leu = PointTransaction.objects.filter(user=request.user, description=f"Leitura: {chapter.title}").exists()

    if not ja_leu:
        with transaction.atomic():
            PointTransaction.objects.create(user=request.user, quantity=xp_leitura, description=f"Leitura: {chapter.title}")
            request.user.xp += xp_leitura
            request.user.save()
            # Cria o registro mas deixa completed_at como None
            UserProgress.objects.get_or_create(user=request.user, chapter=chapter)
            messages.success(request, f"📖 +{xp_leitura} XP pela leitura!")

    return redirect('gamification:exibir_quiz', slug=chapter.slug)

# --- 4. QUIZ (50% XP + CONCLUSÃO REAL) ---
@login_required
def exibir_quiz(request, slug):
    capitulo = get_object_or_404(Chapter, slug=slug)
    questoes = capitulo.questoes.all().prefetch_related('alternativas')
    xp_quiz = int(capitulo.xp_value * 0.5)
    ja_fez = PointTransaction.objects.filter(user=request.user, description=f"Aprovação Quiz: {capitulo.title}").exists()
    
    if request.method == "POST":
        acertos = 0
        total = questoes.count()
        detalhes = []
        for q in questoes:
            alt_id = request.POST.get(f'questao_{q.id}')
            escolha = Alternativa.objects.filter(id=alt_id).first() if alt_id else None
            if escolha and escolha.e_correta: acertos += 1
            detalhes.append({'pergunta': q.enunciado, 'escolha': escolha.texto if escolha else "N/A", 'foi_correta': escolha.e_correta if escolha else False})

        percentual = (acertos / total * 100) if total > 0 else 0
        aprovado = percentual >= 70

        if aprovado:
            with transaction.atomic():
                prog, _ = UserProgress.objects.get_or_create(user=request.user, chapter=capitulo)
                # AJUSTADO: Em vez de .completed = True, usamos .completed_at = timezone.now()
                prog.completed_at = timezone.now()
                prog.save()

                if not ja_fez:
                    PointTransaction.objects.create(user=request.user, quantity=xp_quiz, description=f"Aprovação Quiz: {capitulo.title}")
                    request.user.xp += xp_quiz
                    request.user.save()
                    check_user_medals(request.user)

        return render(request, 'gamification/quiz_resultado.html', {
            'capitulo': capitulo, 'aprovado': aprovado, 'percentual': int(percentual),
            'acertos': acertos, 'total': total, 'resultados': detalhes
        })
    return render(request, 'gamification/quiz.html', {'capitulo': capitulo, 'questoes': questoes})

# --- 5. EXTRAS E HANDLERS ---
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