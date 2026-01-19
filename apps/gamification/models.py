from django.db import models
from django.conf import settings

class Medal(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome da Medalha")
    description = models.TextField(verbose_name="Descrição da Conquista")
    icon = models.ImageField(upload_to='badges/', verbose_name="Ícone/Imagem")
    min_points = models.PositiveIntegerField(verbose_name="Pontos Necessários")

    def __str__(self):
        return self.name

class PointTransaction(models.Model):
    # Relaciona com o Custom User que criamos (Sivaldo, Eralice, etc.)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    quantity = models.IntegerField(verbose_name="Quantidade de Pontos")
    description = models.CharField(max_length=255, verbose_name="Motivo do Ganho")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.quantity} pontos"