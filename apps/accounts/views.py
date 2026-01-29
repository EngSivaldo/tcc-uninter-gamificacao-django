from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import Coalesce
from apps.gamification.models import UserProgress, Trail, UserMedal, PointTransaction, Chapter
from django.utils import timezone

from django.db.models import Count, Q



User = get_user_model()


# --- 2. FORMULÁRIO DE REGISTRO COM RU ---
class StudentRegistrationForm(UserCreationForm):
    ru = forms.CharField(
        label='Registro Acadêmico (RU)', 
        max_length=20, 
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-dark-900/50 border border-white/10 rounded-2xl px-12 py-4 text-white outline-none focus:border-neon/50 transition-all',
            'placeholder': 'Digite seu RU'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('ru',)

# --- 3. VIEW DE REGISTRO ---
def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bem-vindo(a), {user.username}!')
            return redirect('gamification:checkout') 
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})




User = get_user_model()

@login_required
def dashboard(request):
    user = request.user
    
    # 1. Leaderboard Global (Top 5) - Mantido
    ranking = User.objects.all().order_by('-xp')[:5] 
    
    # 2. Log de Operações Recentes - Mantido
    transacoes_recentes = PointTransaction.objects.filter(
        user=user
    ).order_by('-created_at')[:3]

    # 3. Medalhas com select_related (Ótimo para performance) - Mantido
    conquistas = UserMedal.objects.filter(user=user).select_related('medal')

    # 4. ESTATÍSTICAS OTIMIZADAS (Ponto forte para o relatório técnico)
    # Pegamos o total de capítulos do sistema em uma única consulta
    total_chapters_system = Chapter.objects.count()
    
    # Pegamos o total de capítulos que o usuário já completou
    completed_chapters_count = UserProgress.objects.filter(user=user).count()
    
    # Cálculo de Sincronia Global
    overall_progress = int((completed_chapters_count / total_chapters_system * 100)) if total_chapters_system > 0 else 0

    # 5. CÁLCULO DE TRILHAS CONCLUÍDAS (Melhoria de Engenharia)
    # Em vez de um loop manual, pedimos para o banco contar trilhas onde
    # o número de capítulos concluídos é igual ao total de capítulos da trilha.
    trails = Trail.objects.annotate(
        total_ch=Count('chapters', distinct=True),
        done_ch=Count('chapters', filter=Q(chapters__userprogress__user=user), distinct=True)
    )
    
    completed_trails_count = 0
    for t in trails:
        if t.total_ch > 0 and t.total_ch == t.done_ch:
            completed_trails_count += 1

    context = {
        'user': user,
        'ranking': ranking,
        'overall_progress': overall_progress,
        'transacoes_recentes': transacoes_recentes,
        'conquistas': conquistas,
        'total_trails': trails.count(),
        'completed_trails': completed_trails_count,
    }
    
    return render(request, 'accounts/dashboard.html', context)