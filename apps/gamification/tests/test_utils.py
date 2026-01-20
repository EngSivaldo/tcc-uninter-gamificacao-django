from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.gamification.models import Medal, PointTransaction, UserMedal
from apps.gamification.utils import check_user_medals

User = get_user_model()

class UtilsGamificationTest(TestCase):
    def setUp(self):
        # Criamos o usuário e as medalhas de teste
        self.user = User.objects.create_user(username='sivaldo', password='123', ru='4139872')
        self.medal_1 = Medal.objects.create(name="Bronze", description="10 pts", min_points=10)
        self.medal_2 = Medal.objects.create(name="Prata", description="50 pts", min_points=50)

    def test_award_single_medal(self):
        """Testa se o sistema entrega uma medalha quando atinge o XP exato"""
        PointTransaction.objects.create(user=self.user, quantity=10)
        
        # LÓGICA SÊNIOR: Removemos a medalha criada pelo Signal para testar a função utils
        UserMedal.objects.filter(user=self.user).delete()
        
        # Agora sim testamos se a função consegue criar a medalha sozinha
        conquered = check_user_medals(self.user)
        
        self.assertIn("Bronze", conquered)
        self.assertEqual(UserMedal.objects.filter(user=self.user).count(), 1)

    def test_award_multiple_medals(self):
        """Testa se entrega várias medalhas de uma vez se o XP for alto"""
        PointTransaction.objects.create(user=self.user, quantity=100)
        
        # Limpamos o que o Signal fez automaticamente
        UserMedal.objects.filter(user=self.user).delete()
        
        conquered = check_user_medals(self.user)
        
        self.assertIn("Bronze", conquered)
        self.assertIn("Prata", conquered)
        self.assertEqual(len(conquered), 2)

    def test_no_duplicate_medals(self):
        """Garante que a função não entrega a mesma medalha duas vezes (idempotência)"""
        PointTransaction.objects.create(user=self.user, quantity=20)
        check_user_medals(self.user) # Ganha a primeira vez
        
        # Tenta rodar de novo
        conquered_again = check_user_medals(self.user)
        self.assertEqual(len(conquered_again), 0) # Não deve ganhar nada novo