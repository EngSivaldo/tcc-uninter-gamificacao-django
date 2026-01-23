# apps/gamification/domain.py

class IChapterRepository:
    """Esta é a PORTA. Ela diz que precisamos buscar capítulos."""
    def get_chapter_by_slug(self, slug):
        raise NotImplementedError