from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction # Importante para integridade de dados
from .models import Trail, Chapter, PointTransaction, UserProgress
from .utils import check_user_medals
import markdown  # <--- 1. Importação necessária
from django.utils.safestring import mark_safe # Boa prática para templates
from django.shortcuts import render

@login_required
def trail_list(request):
    """Lista todas as trilhas disponíveis."""
    trails = Trail.objects.all()
    return render(request, 'gamification/trail_list.html', {'trails': trails})

@login_required
def trail_detail(request, trail_id):
    """Exibe os capítulos de uma trilha com cálculo de progresso."""
    trail = get_object_or_404(Trail, id=trail_id)
    chapters = trail.chapters.all()
    
    # Lógica Sênior: Cálculo de Progresso
    total_chapters = chapters.count()
    completed_chapters = UserProgress.objects.filter(
        user=request.user, 
        chapter__trail=trail
    ).count()
    
    # Evita divisão por zero se a trilha estiver vazia
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
def chapter_detail(request, chapter_id):
    """Exibe o conteúdo da aula com tratamento de erros e fallback."""
    chapter = get_object_or_404(Chapter, id=chapter_id)
    
    # 1. Tratamento de Segurança: Evita erro se o conteúdo for None
    raw_content = chapter.content or ""
    
    try:
        # 2. Conversão com tratamento de exceções
        html_output = markdown.markdown(
            raw_content, 
            extensions=[
                'fenced_code',  # Suporte a blocos de código com ```
                'codehilite',   # Destaque de sintaxe
                'tables',       # Suporte a tabelas Markdown
                'toc'           # Gera Sumário se houver [TOC] no texto
            ]
        )
        # 3. Injeção segura: Criamos o atributo 'content_html' dinamicamente
        chapter.content_html = mark_safe(html_output)
        
    except Exception as e:
        # Fallback caso a biblioteca Markdown falhe por algum motivo técnico
        print(f"Erro na renderização do Markdown: {e}")
        chapter.content_html = mark_safe(f"<p class='text-red-500'>Erro ao carregar conteúdo técnico. Por favor, contate o suporte.</p>")

    return render(request, 'gamification/chapter_detail.html', {'chapter': chapter})

@login_required
def complete_chapter(request, chapter_id):
    """
    Lógica sênior:
    - Garante idempotência (não ganha XP duas vezes)
    - Usa transaction.atomic para consistência total
    - Sincroniza XP, progresso e medalhas de forma segura
    """
    chapter = get_object_or_404(Chapter, id=chapter_id)
    user = request.user

    # 1. Verificação de integridade (idempotência)
    already_done = PointTransaction.objects.filter(
        user=user,
        description=f"Conclusão: {chapter.title}"
    ).exists()

    if already_done:
        messages.warning(request, "Você já recebeu XP por esta aula anteriormente.")
        return redirect('gamification:trail_detail', trail_id=chapter.trail.id)

    try:
        # 2. Transação atômica
        with transaction.atomic():

            # Registra o progresso do usuário
            UserProgress.objects.get_or_create(
                user=user,
                chapter=chapter
            )

            # Registra a transação de pontos
            PointTransaction.objects.create(
                user=user,
                quantity=chapter.xp_value,
                description=f"Conclusão: {chapter.title}"
            )

            # Atualiza o XP do usuário
            user.xp += chapter.xp_value
            user.save(update_fields=["xp"])

            # 3. Verifica e concede medalhas
            novas_conquistas = check_user_medals(user)

        # 4. Feedback ao usuário (fora da transação)
        if novas_conquistas:
            medalhas_str = ", ".join(novas_conquistas)
            messages.success(
                request,
                f"🏆 Incrível! +{chapter.xp_value} XP e novas medalhas conquistadas: {medalhas_str}!"
            )
        else:
            messages.success(
                request,
                f"✅ Aula concluída com sucesso! Você ganhou {chapter.xp_value} XP."
            )

    except Exception as e:
        messages.error(
            request,
            "Ocorreu um erro ao processar sua recompensa. Tente novamente."
        )
        print(f"[ERRO GAMIFICAÇÃO] {e}")

    return redirect('gamification:trail_detail', trail_id=chapter.trail.id)


def error_404(request, exception):
    """View personalizada para erro 404 (Não Encontrado)"""
    return render(request, '404.html', status=404)

def error_500(request):
    """View personalizada para erro 500 (Erro Interno do Servidor)"""
    return render(request, '500.html', status=500)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required # Somente alunos logados podem pagar
def checkout(request):
    return render(request, 'gamification/checkout.html')