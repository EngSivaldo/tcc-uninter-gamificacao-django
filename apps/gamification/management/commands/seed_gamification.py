from django.core.management.base import BaseCommand
from gamification.models import Trail, Chapter

class Command(BaseCommand):
    help = "Popula trilhas e capítulos de Engenharia de Software"

    def handle(self, *args, **kwargs):

        trails = [
            {
                "title": "Engenharia de Software: Fundamentos e Prática",
                "description": (
                    "Introdução aos fundamentos da Engenharia de Software, "
                    "abordando ciclo de vida, requisitos, modelagem e desenvolvimento web."
                ),
                "chapters": [
                    ("Introdução à Engenharia de Software", "Conceitos básicos, histórico e importância da Engenharia de Software.", 50),
                    ("Ciclo de Vida do Software", "Modelos de desenvolvimento como cascata, incremental e iterativo.", 50),
                    ("Metodologias Tradicionais e Ágeis", "Comparação entre métodos clássicos e metodologias ágeis.", 60),
                    ("Levantamento de Requisitos", "Técnicas para coleta e análise de requisitos.", 60),
                    ("Modelagem UML", "Diagramas UML e sua aplicação prática.", 70),
                    ("Introdução ao Django", "Apresentação do framework Django e suas vantagens.", 80),
                    ("Arquitetura MVT", "Entendendo o padrão Model-View-Template.", 80),
                ],
            },
            {
                "title": "Análise e Projeto de Sistemas",
                "description": (
                    "Estudo aprofundado da análise, documentação e projeto "
                    "de sistemas orientados a objetos."
                ),
                "chapters": [
                    ("Análise de Sistemas", "Papel do analista de sistemas e visão geral.", 50),
                    ("Stakeholders e Requisitos", "Identificação e gestão de stakeholders.", 60),
                    ("Casos de Uso", "Modelagem de requisitos com casos de uso.", 70),
                    ("Diagramas UML", "Diagramas estruturais e comportamentais.", 80),
                    ("Projeto de Software", "Transformando requisitos em soluções técnicas.", 90),
                    ("Padrões de Projeto", "Aplicação de design patterns.", 100),
                ],
            },
            {
                "title": "Arquitetura e Padrões de Software",
                "description": (
                    "Conceitos arquiteturais, boas práticas e padrões "
                    "utilizados em sistemas modernos."
                ),
                "chapters": [
                    ("Arquitetura de Software", "Fundamentos e conceitos-chave.", 60),
                    ("Arquitetura em Camadas", "Separação de responsabilidades.", 70),
                    ("MVC, MVT e Clean Architecture", "Comparação de arquiteturas.", 80),
                    ("Princípios SOLID", "Boas práticas de design orientado a objetos.", 90),
                    ("Design Patterns GoF", "Padrões clássicos de projeto.", 100),
                    ("Arquitetura Escalável", "Preparando sistemas para crescimento.", 120),
                ],
            },
            {
                "title": "Qualidade de Software e Testes",
                "description": (
                    "Garantia de qualidade, testes e validação de sistemas de software."
                ),
                "chapters": [
                    ("Qualidade de Software", "Conceitos e atributos de qualidade.", 50),
                    ("Tipos de Testes", "Testes unitários, integração e sistema.", 60),
                    ("Testes Unitários", "Automatização e boas práticas.", 80),
                    ("Testes de Integração", "Validação entre módulos.", 90),
                    ("Automação de Testes", "Ferramentas e estratégias.", 100),
                    ("Métricas de Qualidade", "Medição e melhoria contínua.", 110),
                ],
            },
            {
                "title": "Gerência de Projetos de Software",
                "description": (
                    "Planejamento, execução e controle de projetos de software."
                ),
                "chapters": [
                    ("Introdução à Gerência de Projetos", "Visão geral e conceitos.", 50),
                    ("PMBOK e SCRUM", "Modelos de gestão tradicionais e ágeis.", 70),
                    ("Planejamento do Projeto", "Cronograma, escopo e custos.", 80),
                    ("Gestão de Riscos", "Identificação e mitigação de riscos.", 90),
                    ("Métricas e Indicadores", "Acompanhamento de desempenho.", 100),
                    ("Encerramento do Projeto", "Entrega e lições aprendidas.", 110),
                ],
            },
        ]

        for trail_data in trails:
            trail, created = Trail.objects.get_or_create(
                title=trail_data["title"],
                defaults={"description": trail_data["description"]}
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Trilha criada: {trail.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠ Trilha já existe: {trail.title}"))

            for index, (title, content, xp) in enumerate(trail_data["chapters"], start=1):
                Chapter.objects.get_or_create(
                    trail=trail,
                    order=index,
                    title=f"Aula {index:02d} - {title}",
                    defaults={
                        "content": content,
                        "xp_value": xp
                    }
                )

        self.stdout.write(self.style.SUCCESS("🎯 Trilhas e capítulos criados com sucesso!"))
