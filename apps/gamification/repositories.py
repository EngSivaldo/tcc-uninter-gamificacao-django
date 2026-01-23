# apps/gamification/repositories.py
from .models import Chapter
from .domain import IChapterRepository

class DjangoChapterRepository(IChapterRepository):
    """Este é o ADAPTADOR. Ele usa o Django para falar com o banco."""
    def get_chapter_by_slug(self, slug):
        return Chapter.objects.get(slug=slug)