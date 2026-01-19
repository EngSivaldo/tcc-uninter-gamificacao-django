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
    


class Trail(models.Model):
    """Representa uma matéria ou trilha de conhecimento."""
    title = models.CharField(max_length=200, verbose_name="Título da Trilha")
    description = models.TextField(verbose_name="Descrição")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Chapter(models.Model):
    trail = models.ForeignKey(Trail, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200, verbose_name="Título do Capítulo")
    
    # NOVO CAMPO:
    video_url = models.URLField(blank=True, null=True, verbose_name="URL da Vídeo Aula (YouTube/Vimeo)")
    
    content = models.TextField(verbose_name="Conteúdo da Aula")
    xp_value = models.PositiveIntegerField(default=50, verbose_name="Valor em XP")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem de exibição")

    # Método Sênior: Extrai o ID do YouTube para o Embed automático
    @property
    def youtube_id(self):
        if "youtube.com" in self.video_url or "youtu.be" in self.video_url:
            import re
            # Expressão regular para capturar o ID do vídeo
            regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
            match = re.search(regex, self.video_url)
            return match.group(1) if match else None
        return None

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.trail.title} - {self.title}"
    
    
class UserMedal(models.Model):
    """Registra o momento em que um aluno conquista uma medalha específica."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='earned_medals')
    medal = models.ForeignKey(Medal, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'medal') # Impede que o aluno ganhe a mesma medalha duas vezes

    def __str__(self):
        return f"{self.user.username} conquistou {self.medal.name}"