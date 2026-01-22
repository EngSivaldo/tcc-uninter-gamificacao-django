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
    
    # Padronizando para 'xp' para bater com a lógica da View e Utils
    xp = models.PositiveIntegerField(
        default=0, 
        verbose_name="Saldo de XP"
    )

    def __str__(self):
        return f"{self.username} (RU: {self.ru})"

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"