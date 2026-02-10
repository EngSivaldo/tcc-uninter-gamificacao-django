from django.contrib.auth.models import AbstractUser
from django.db import models
        
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.gamification.models import Trail, UserProgress, PointTransaction, UserMedal
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
        return self.is_plus or self.is_staff

    @property
    def rank(self):
        """
        Lógica de Patente 'Elite' baseada em XP.
        Retorna um dicionário com Nome, Cor (Tailwind) e Ícone (FontAwesome).
        """
        if self.xp >= 5000:
            return {'name': 'Staff Engineer', 'color': 'violet-500', 'icon': 'fa-trophy'}
        if self.xp >= 1500:
            return {'name': 'Senior Developer', 'color': 'accent', 'icon': 'fa-microchip'}
        if self.xp >= 500:
            return {'name': 'Lead Developer', 'color': 'neon', 'icon': 'fa-code'}
        
        return {'name': 'Junior Developer', 'color': 'slate-400', 'icon': 'fa-seedling'}

    def __str__(self):
        return f"{self.username} (RU: {self.ru})"

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['-date_joined']
        
    @property
    def rank(self):
        """
        Retorna a Patente ATUAL do usuário baseada no XP.
        """
        if self.xp >= 1000:
            return {'name': 'Arquiteto de Sistemas', 'color': 'violet-500', 'icon': 'fa-crown'}
        elif self.xp >= 500:
            return {'name': 'Engenheiro de Software I', 'color': 'accent', 'icon': 'fa-user-gear'}
        elif self.xp >= 250:
            return {'name': 'Programador Senior', 'color': 'neon', 'icon': 'fa-code-branch'}
        elif self.xp >= 100:
            return {'name': 'Programador Junior', 'color': 'blue-400', 'icon': 'fa-code'}
        
        return {'name': 'Junior Developer', 'color': 'slate-400', 'icon': 'fa-seedling'}

    @property
    def next_rank_data(self):
        """
        Calcula os dados para a barra de progresso da PRÓXIMA patente.
        """
        if self.xp < 100:
            goal = 100
            label = "Programador Junior"
        elif self.xp < 250:
            goal = 250
            label = "Programador Senior"
        elif self.xp < 500:
            goal = 500
            label = "Engenheiro de Software I"
        elif self.xp < 1000:
            goal = 1000
            label = "Arquiteto de Sistemas"
        else:
            # Caso o usuário ultrapasse 1000 XP
            return {'percent': 100, 'missing': 0, 'next_label': "Nível Máximo", 'is_max': True}

        # Cálculo matemático para a barra de progresso visual
        # Fórmula: (XP Atual / Meta) * 100
        percent = int((self.xp / goal) * 100) if goal > 0 else 0
        
        return {
            'percent': percent,
            'missing': goal - self.xp,
            'next_label': label,
            'is_max': False
        }
        


User = get_user_model()

@login_required
def dashboard(request):
    user = request.user
    
    # 1. Ranking Global (Sincronizado com o HTML)
    ranking = User.objects.order_by('-xp')[:5]
    
    # 2. Log de Operações
    transacoes_recentes = PointTransaction.objects.filter(
        user=user
    ).order_by('-created_at')[:3]
    
    # 3. Medalhas
    conquistas = UserMedal.objects.filter(user=user).select_related('medal')
    
    # 4. Cálculo de Sincronia Global (Barra Central)
    user_progress = UserProgress.objects.filter(user=user)
    total_trails = Trail.objects.count()
    
    if total_trails > 0:
        # Soma o progresso de cada trilha e tira a média
        total_percent = sum([p.calculate_progress() for p in user_progress if hasattr(p, 'calculate_progress')])
        overall_progress = int(total_percent / total_trails) if total_trails > 0 else 0
    else:
        overall_progress = 0

    context = {
        'user': user,
        'ranking': ranking,
        'overall_progress': overall_progress,
        'transacoes_recentes': transacoes_recentes,
        'conquistas': conquistas,
    }
    
    return render(request, 'accounts/dashboard.html', context)