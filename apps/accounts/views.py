from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 1. Soma Real de Pontos do Banco
        total = self.request.user.transactions.aggregate(total=Sum('quantity'))['total'] or 0
        
        # 2. Lógica de Nível (Meta de 500 XP para subir de nível)
        goal = 500 
        progress_percentage = (total / goal) * 100 if total < goal else 100
        
        context['total_points'] = total
        context['progress'] = progress_percentage # Envia a porcentagem real para o HTML
        return context