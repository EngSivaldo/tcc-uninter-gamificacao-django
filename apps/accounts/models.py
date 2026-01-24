from django.contrib.auth.models import AbstractUser
from django.db import models
        
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.gamification.models import Trail, UserProgress
from django.contrib.auth import get_user_model

class User(AbstractUser):
    """
    Modelo de Usuário Customizado para a plataforma Gamifica UNINTER.
    """
    
    # --- CAMADA ACADÊMICA ---
    ru = models.CharField(
        max_length=15, 
        unique=True, 
        verbose_name="Registro Universitário (RU)",
        help_text="Identificador único do aluno para o TCC."
    )
    
    # --- CAMADA DE GAMIFICAÇÃO ---
    xp = models.PositiveIntegerField(
        default=0, 
        verbose_name="Saldo de XP acumulado"
    )

    # --- CAMADA PROFISSIONAL ---
    is_plus = models.BooleanField(
        default=False, 
        verbose_name="Assinante Plus"
    )

    @property
    def is_premium_member(self):
        """Retorna True se o usuário for assinante ou administrador."""
        # Corrigido: self.is_is_staff removido por self.is_staff
        return self.is_plus or self.is_staff

    def get_rank(self):
        """Lógica de Patente baseada em XP para o Dashboard."""
        if self.xp >= 1000: return "Staff Engineer"
        if self.xp >= 500: return "Senior Developer"
        if self.xp >= 200: return "Lead Developer"
        return "Junior Developer"

    def __str__(self):
        return f"{self.username} (RU: {self.ru})"

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['-date_joined']
        


User = get_user_model()

@login_required
def dashboard(request):
    user = request.user
    
    # 1. Pega o progresso do usuário (para a barra de Sincronia)
    user_progress = UserProgress.objects.filter(user=user)
    
    # 2. Leaderboard Global: Pega os 5 melhores alunos por XP
    leaderboard = User.objects.order_by('-xp')[:5]
    
    # 3. Estatísticas rápidas
    total_trails = Trail.objects.count()
    completed_trails = user_progress.filter(completed=True).count()
    
    # 4. Cálculo de Sincronia Global (Média de progresso de todas as trilhas)
    # Se você tiver 2 trilhas e completou 50% de cada, sua sincronia é 50%
    if total_trails > 0:
        total_percent = sum([p.calculate_progress() for p in user_progress])
        sincronia_global = total_percent / total_trails
    else:
        sincronia_global = 0

    context = {
        'user': user,
        'leaderboard': leaderboard,
        'sincronia_global': sincronia_global,
        'completed_trails': completed_trails,
        'total_trails': total_trails,
        'progress_list': user_progress,
    }
    
    return render(request, 'accounts/dashboard.html', context)