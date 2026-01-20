from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from gamification.models import UserMedal  # Importe o modelo das medalhas

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Soma Real de Pontos do Banco (XP Total)
        total = self.request.user.transactions.aggregate(total=Sum('quantity'))['total'] or 0
        
        # 2. Lógica de Nível (Meta de 1000 XP para este exemplo)
        goal = 1000 
        progress_percentage = (total / goal) * 100 if total < goal else 100

        # 3. Busca de Medalhas Conquistadas (Novidade da Sprint 4)
        # Buscamos as medalhas vinculadas ao usuário logado
        conquistas = UserMedal.objects.filter(user=self.request.user).order_by('-earned_at')

        # Envia tudo para o HTML
        context['total_points'] = total
        context['progress'] = progress_percentage
        context['conquistas'] = conquistas
        
        return context