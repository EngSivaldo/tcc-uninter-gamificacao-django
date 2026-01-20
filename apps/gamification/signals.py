from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from .models import PointTransaction, Medal, UserMedal

@receiver(post_save, sender=PointTransaction)
def check_user_medals(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        # 1. Calcula o XP Total atual do usuário
        total_xp = PointTransaction.objects.filter(user=user).aggregate(total=Sum('quantity'))['total'] or 0
        
        # 2. Busca medalhas que o usuário atingiu o XP mas ainda NÃO possui
        # Usamos o campo 'min_points' que confirmamos no seu model
        medalhas_disponiveis = Medal.objects.filter(
            min_points__lte=total_xp
        ).exclude(
            id__in=UserMedal.objects.filter(user=user).values_list('medal_id', flat=True)
        )
        
        # 3. Registra as novas conquistas
        for medalha in medalhas_disponiveis:
            UserMedal.objects.get_or_create(user=user, medal=medalha)