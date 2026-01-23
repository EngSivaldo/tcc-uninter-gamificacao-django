from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from apps.gamification.models import UserMedal
from .models import User
# Importe o modelo 
from django.contrib.auth import login # Importante para logar o aluno na hora
from django.contrib.auth import get_user_model
# Arquivo: apps/accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User # Certifique-se que seu modelo User tem o campo 'ru'

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
        
        # LÓGICA DO RANKING (Sprint 5)
          # Busca os usuários, soma suas transações e ordena pelo     total de pontos
        ranking = User.objects.annotate(
            total_xp=Sum('transactions__quantity')
        ).order_by('-total_xp')[:5] # Pega apenas os 5 melhores


        # Envia tudo para o HTML
        context['total_points'] = total
        context['progress'] = progress_percentage
        context['conquistas'] = conquistas
        context['ranking'] = ranking
        
        return context
      
# 1. Criamos um formulário que inclui o campo RU
class StudentRegistrationForm(UserCreationForm):
    ru = forms.CharField(label='Registro Acadêmico (RU)', max_length=20, 
                         widget=forms.TextInput(attrs={'class': 'w-full bg-dark-900/50 border border-white/10 rounded-2xl px-12 py-4 text-white outline-none'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('ru',)

# 2. Atualizamos a view para usar este novo formulário
def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # LOGAR AUTOMATICAMENTE: O aluno já entra logado para pagar
            login(request, user) 
            messages.success(request, 'Conta criada com sucesso! Selecione sua forma de pagamento.')
            # REDIRECIONAMENTO: Agora vai para o checkout que criaremos abaixo
            return redirect('gamification:checkout') 
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})