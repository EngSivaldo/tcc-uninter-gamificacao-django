# apps/gamification/utils.py
from django.db.models import Sum
from .models import PointTransaction, Medal, UserMedal

def check_user_medals(user):
    """
    Analisa o saldo de XP e entrega medalhas pendentes.
    Implementa o gatilho do RF04.
    """
    # 1. Calcula o XP total
    total_xp = PointTransaction.objects.filter(user=user).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # 2. Busca medalhas que o usuário ainda não possui e atingiu a pontuação
    new_available_medals = Medal.objects.exclude(
        id__in=UserMedal.objects.filter(user=user).values_list('medal_id', flat=True)
    ).filter(min_points__lte=total_xp)

    # 3. Registra as conquistas
    conquered_names = []
    for medal in new_available_medals:
        UserMedal.objects.create(user=user, medal=medal)
        conquered_names.append(medal.name)
        
    return conquered_names