from django.db import models
from django.conf import settings
from django.utils.text import slugify

# Mixin para evitar repetição de campos de data (DRY - Don't Repeat Yourself)
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Medal(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome da Medalha")
    description = models.TextField(verbose_name="Descrição da Conquista")
    icon = models.ImageField(upload_to='badges/', verbose_name="Ícone/Imagem")
    min_points = models.PositiveIntegerField(verbose_name="Pontos Necessários")

    def __str__(self):
        return self.name

class PointTransaction(models.Model):
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

class Trail(TimestampedModel):
    title = models.CharField(max_length=200, verbose_name="Título da Trilha")
    # Ajuste Sênior: unique=False e null=True para evitar o IntegrityError inicial
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    description = models.TextField(verbose_name="Descrição")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

import re
from django.db import models
from django.utils.text import slugify
# Certifique-se de que o TimestampedModel está importado corretamente do seu core/models
# from apps.core.models import TimestampedModel 

class Chapter(TimestampedModel):
    trail = models.ForeignKey('Trail', on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200, verbose_name="Título do Capítulo")
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL da Vídeo Aula")
    content = models.TextField(blank=True, null=True)
    xp_value = models.PositiveIntegerField(default=50, verbose_name="Valor em XP")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem")

    @property
    def youtube_id(self):
        """
        Extrai o ID do vídeo do YouTube a partir da video_url.
        Suporta diversos formatos de link (curto, longo, embed).
        """
        if not self.video_url:
            return None
        
        # Regex para capturar os 11 caracteres do ID do YouTube
        regex = r'(?:v=|\/|be\/|embed\/)([a-zA-Z0-9_-]{11})'
        match = re.search(regex, self.video_url)
        
        return match.group(1) if match else None

    def save(self, *args, **kwargs):
        # 1. LÓGICA DE SEQUENCIAMENTO (Apenas para novos registros)
        if not self.pk:  
            if self.order == 0:
                last_order = Chapter.objects.filter(trail=self.trail).count()
                self.order = last_order + 1
            
            # Formata o título automaticamente para o padrão "Aula 01 - Nome"
            if not self.title.startswith("Aula"):
                self.title = f"Aula {self.order:02d} - {self.title}"

        # 2. LÓGICA DE SLUG E ANTI-COLISÃO
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Chapter.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # 3. SALVAMENTO FINAL
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['order']
        # Impede títulos duplicados DENTRO da mesma trilha
        unique_together = ('trail', 'title') 
        verbose_name = "Capítulo"
        verbose_name_plural = "Capítulos"
        
    class Meta:
        ordering = ['order']
        # Regra Sênior: Impede títulos duplicados DENTRO da mesma trilha
        unique_together = ('trail', 'title') 
        verbose_name = "Capítulo"

    @property
    def youtube_id(self):
        if self.video_url and ("youtube.com" in self.video_url or "youtu.be" in self.video_url):
            import re
            regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
            match = re.search(regex, self.video_url)
            return match.group(1) if match else None
        return None

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.trail.title} - {self.title}"

class UserMedal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='earned_medals'
    )
    medal = models.ForeignKey(Medal, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name="Data da Conquista")

    class Meta:
        unique_together = ('user', 'medal')
        verbose_name = "Medalha do Usuário"

    def __str__(self):
        return f"{self.user.username} - {self.medal.name}"

class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'chapter')
        verbose_name = "Progresso do Aluno"