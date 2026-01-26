from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import Coalesce
from apps.gamification.models import UserMedal, Trail, UserProgress # Garanta que Medal esteja aqui
from django.utils import timezone

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



@login_required
def dashboard(request):
    user = request.user
    
    # 1. Busca capítulos concluídos
    completed_chapters = UserProgress.objects.filter(user=user).select_related('chapter__trail')
    
    # 2. Leaderboard Global (AJUSTADO PARA USAR O CAMPO XP DIRETO)
    # Ordenamos pelo campo 'xp' do seu modelo User
    ranking = User.objects.all().order_by('-xp')[:5] 
    
    # 3. Estatísticas de Trilhas
    trails = Trail.objects.all()
    total_trails_count = trails.count()
    
    completed_trails_count = 0
    for trail in trails:
        total_chapters_in_trail = trail.chapters.count()
        done_in_trail = completed_chapters.filter(chapter__trail=trail).count()
        if total_chapters_in_trail > 0 and done_in_trail == total_chapters_in_trail:
            completed_trails_count += 1
    
    # 4. Cálculo de Sincronia Global
    total_chapters_system = sum([t.chapters.count() for t in trails])
    sincronia_global = (completed_chapters.count() / total_chapters_system * 100) if total_chapters_system > 0 else 0

    # 5. Conquistas (Medalhas)
    conquistas = UserMedal.objects.filter(user=user).select_related('medal').order_by('-earned_at')

    context = {
        'user': user,
        'ranking': ranking, # Agora com XP real do campo .xp
        'conquistas': conquistas,
        'total_points': user.xp,
        'progress': sincronia_global,
        'total_trails': total_trails_count,
        'completed_trails': completed_trails_count,
    }
    
    return render(request, 'accounts/dashboard.html', context)