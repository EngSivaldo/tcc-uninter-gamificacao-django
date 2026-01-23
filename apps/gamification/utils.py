from django.db.models import Sum
from django.db import transaction
from typing import List
from .models import PointTransaction, Medal, UserMedal

def check_user_medals(user) -> List[str]:
    """
    Motor de Conquistas Otimizado:
    - Calcula o saldo real de XP via transações.
    - Identifica medalhas não conquistadas de forma performática.
    - Registra novas conquistas em lote (bulk_create).
    """
    
    # 1. Recupera o XP total acumulado através do histórico de transações
    # Usamos o aggregate para processamento direto no banco de dados (mais rápido)
    total_xp = PointTransaction.objects.filter(user=user).aggregate(
        Sum('quantity')
    )['quantity__sum'] or 0
    
    # 2. Busca IDs de medalhas que o usuário já conquistou para evitar duplicidade
    earned_medal_ids = UserMedal.objects.filter(user=user).values_list('medal_id', flat=True)

    # 3. Filtra medalhas que o usuário atingiu o critério mas ainda não possui
    new_available_medals = Medal.objects.exclude(
        id__in=earned_medal_ids
    ).filter(min_points__lte=total_xp)

    conquered_names = []
    new_user_medals = []

    # 4. Prepara os objetos para inserção em lote
    for medal in new_available_medals:
        new_user_medals.append(UserMedal(user=user, medal=medal))
        conquered_names.append(medal.name)

    # 5. Lógica Sênior: Bulk Create (Uma única transação para N medalhas)
    if new_user_medals:
        UserMedal.objects.bulk_create(new_user_medals)
        
    return conquered_names