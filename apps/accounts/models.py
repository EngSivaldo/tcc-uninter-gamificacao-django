from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Campo obrigatório para o TCC da UNINTER
    ru = models.CharField(
        max_length=15, 
        unique=True, 
        verbose_name="Registro Universitário (RU)",
        help_text="Insira o RU do aluno."
    )
    
    # Campo base para o motor de gamificação
    points = models.PositiveIntegerField(
        default=0, 
        verbose_name="Saldo de Pontos"
    )

    def __str__(self):
        return f"{self.username} (RU: {self.ru})"

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"