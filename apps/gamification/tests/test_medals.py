from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.gamification.models import Medal, UserMedal, PointTransaction

User = get_user_model()

class MedalLogicTest(TestCase):
    def setUp(self):
        # 1. Criamos um usuário de teste
        self.user = User.objects.create_user(
            username='teststudent', 
            password='password123', 
            ru='1234567'
        )
        
        # 2. Criamos a medalha usando o campo correto: min_points
        self.medal = Medal.objects.create(
            name="Desbravador",
            description="Ganhou 100 pontos",
            min_points=100  # <--- AJUSTADO PARA O SEU MODELO
        )

    def test_medal_activation(self):
        """Valida se o usuário ganha a medalha ao atingir o XP necessário"""
        # 3. Simulamos o ganho de 100 pontos
        PointTransaction.objects.create(user=self.user, quantity=100)
        
        # 4. Verificamos se o sistema de gatilho registrou a conquista
        has_medal = UserMedal.objects.filter(user=self.user, medal=self.medal).exists()
        
        # 5. Afirmação final (Assert): Se for True, o teste passa!
        self.assertTrue(has_medal, "A medalha deveria ter sido entregue ao atingir 100 XP")
        
        
from django.urls import reverse

class GamificationIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='aluno_teste', password='123', ru='4139872')
        self.client.login(username='aluno_teste', password='123')

    def test_dashboard_access(self):
        """Verifica se a Dashboard carrega corretamente para o aluno"""
        # AJUSTADO: Adicionamos o namespace 'accounts:' antes do nome da rota
        response = self.client.get(reverse('accounts:dashboard')) 
        
        self.assertEqual(response.status_code, 200)
        # Verifica se o template carregou algum elemento esperado
        self.assertContains(response, "Ranking")