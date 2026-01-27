import re
from django.db import models
from django.conf import settings
from django.utils.text import slugify

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    quantity = models.IntegerField(verbose_name="Quantidade de Pontos")
    description = models.CharField(max_length=255, verbose_name="Motivo do Ganho")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.quantity} pontos"

class Trail(TimestampedModel):
    title = models.CharField(max_length=200, verbose_name="Título da Trilha")
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    description = models.TextField(verbose_name="Descrição")
    image = models.ImageField(upload_to='trails/', blank=True, null=True)
    total_xp = models.IntegerField(default=0)
    is_premium = models.BooleanField(default=False, verbose_name="Trilha Premium")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Chapter(TimestampedModel):
    trail = models.ForeignKey(Trail, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200, verbose_name="Título do Capítulo")
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL da Vídeo Aula")
    content = models.TextField(blank=True, null=True, verbose_name="Conteúdo Markdown")
    xp_value = models.PositiveIntegerField(default=50, verbose_name="Valor em XP")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    # Se você quer que o visitante veja o preview, 
    # algumas aulas precisam ser is_premium=False, ou mude a lógica do template.
    is_premium = models.BooleanField(default=True, verbose_name="Conteúdo Pago")

    @property
    def youtube_id(self):
        if not self.video_url:
            return None
        regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
        match = re.search(regex, self.video_url)
        return match.group(1) if match else None

    def save(self, *args, **kwargs):
        # Evita duplicar "Aula 01 - Aula 01" ao salvar múltiplas vezes
        if not self.pk:
            if self.order == 0:
                self.order = Chapter.objects.filter(trail=self.trail).count() + 1
            
            clean_title = self.title.replace(f"Aula {self.order:02d} - ", "")
            self.title = f"Aula {self.order:02d} - {clean_title}"

        if not self.slug:
            self.slug = slugify(self.title)
            # Lógica simples de slug único (melhorada)
            original_slug = self.slug
            queryset = Chapter.objects.all()
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            
            counter = 1
            while queryset.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']
        unique_together = ('trail', 'title') 
        verbose_name = "Capítulo"
        verbose_name_plural = "Capítulos"

    def __str__(self):
        return f"{self.trail.title} - {self.title}"
    
    # Dentro da classe Chapter
    def is_unlocked(self, user):
        """
        Verifica se este capítulo está desbloqueado para um utilizador específico.
        """
        # Se for a primeira aula (order=1), está sempre desbloqueada
        if self.order <= 1:
            return True
        
        # Busca o capítulo anterior na mesma trilha
        previous_chapter = Chapter.objects.filter(
            trail=self.trail, 
            order__lt=self.order
        ).order_by('-order').first()

        if not previous_chapter:
            return True # Fallback caso não encontre o anterior

        # Verifica se existe progresso registado para o capítulo anterior
        from .models import UserProgress # Import local para evitar importação circular
        return UserProgress.objects.filter(user=user, chapter=previous_chapter).exists()

class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        unique_together = ('user', 'chapter')
        ordering = ['-updated_at'] 
        verbose_name = "Progresso do Aluno"
        verbose_name_plural = "Progressos dos Alunos"
        
        
class UserMedal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='earned_medals')
    medal = models.ForeignKey(Medal, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name="Data da Conquista")

    class Meta:
        unique_together = ('user', 'medal')
        verbose_name = "Medalha do Usuário"
        verbose_name_plural = "Medalhas dos Usuários"

    def __str__(self):
        return f"{self.user.username} - {self.medal.name}"
    
    
    
class Questao(TimestampedModel):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='questoes')
    enunciado = models.TextField(verbose_name="Pergunta")
    xp_recompensa = models.PositiveIntegerField(default=10, verbose_name="XP por Acerto")

    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"

    def __str__(self):
        return f"Pergunta: {self.enunciado[:50]}..."

class Alternativa(models.Model):
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name='alternativas')
    texto = models.CharField(max_length=255, verbose_name="Texto da Alternativa")
    e_correta = models.BooleanField(default=False, verbose_name="É a resposta correta?")

    class Meta:
        verbose_name = "Alternativa"
        verbose_name_plural = "Alternativas"

    def __str__(self):
        return self.texto