from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modelo de Usuário Customizado para a plataforma Gamifica UNINTER.
    Integra requisitos acadêmicos, lógica de gamificação e regras de negócio para monetização.
    """
    
    # --- CAMADA ACADÊMICA (Obrigatório UNINTER) ---
    ru = models.CharField(
        max_length=15, 
        unique=True, 
        verbose_name="Registro Universitário (RU)",
        help_text="Identificador único do aluno para o TCC."
    )
    
    # --- CAMADA DE GAMIFICAÇÃO ---
    xp = models.PositiveIntegerField(
        default=0, 
        verbose_name="Saldo de XP acumulado"
    )

    # --- CAMADA PROFISSIONAL (Business Logic / Monetização) ---
    is_plus = models.BooleanField(
        default=False, 
        verbose_name="Assinante Plus",
        help_text="Define se o usuário possui acesso liberado aos conteúdos Premium."
    )

    # Dica de Senior: Helper para facilitar verificações em templates e views
    @property
    def is_premium_member(self):
        """Retorna True se o usuário for assinante ou superusuário (staff)."""
        return self.is_plus or self.is_is_staff

    def __str__(self):
        return f"{self.username} (RU: {self.ru})"

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['-date_joined']