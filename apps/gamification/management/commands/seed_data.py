from django.core.management.base import BaseCommand
from apps.gamification.models import Trail, Chapter, Medal
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Sincroniza superusuários e popula dados do TCC'

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Atualizando credenciais e carga de dados...")
        
        User = get_user_model()

        # --- 0. CONFIGURAÇÃO DE SIVALDO E ERALICE ---
        users_to_sync = [
            {
                "username": "sivaldo",
                "email": "sivaldovieiradealmeida@gmail.com",
                "ru": "4139872"
            },
            {
                "username": "eralice",
                "email": "AliceMoraesBaia@gmail.com", # E-mail atualizado
                "ru": "4144099"
            }
        ]

        for data in users_to_sync:
            # Sincroniza pelo RU (único). Se existir, atualiza; se não, cria.
            user, created = User.objects.update_or_create(
                ru=data["ru"],
                defaults={
                    "username": data["username"],
                    "email": data["email"],
                    "is_staff": True,
                    "is_superuser": True,
                }
            )
            
            # Define a senha padrão para ambos
            user.set_password("uninter123")
            user.save()

            acao = "criado" if created else "sincronizado"
            self.stdout.write(self.style.SUCCESS(f"✅ Usuário {data['username']} {acao} com sucesso!"))

        # --- 1. TRILHAS E CONTEÚDO (Idempotente) ---
        trails_data = [
            {
                "title": "Dominando Python e Django",
                "desc": "Do zero ao primeiro sistema web profissional.",
                "chapters": [
                    ("Fundamentos do Python", "Sintaxe, listas e dicionários."),
                    ("Django Framework", "MVT, Admin e ORM."),
                ]
            }
        ]

        for t in trails_data:
            trail, _ = Trail.objects.get_or_create(title=t["title"], description=t["desc"])
            for i, (cap_title, cap_cont) in enumerate(t["chapters"], 1):
                Chapter.objects.get_or_create(
                    trail=trail, 
                    title=cap_title, 
                    content=cap_cont, 
                    order=i
                )

        # --- 2. MEDALHAS ---
        Medal.objects.get_or_create(
            name="Engenheiro de Software", 
            description="Finalizou as trilhas básicas.", 
            min_points=150
        )

        self.stdout.write(self.style.SUCCESS('🏁 Processo finalizado. Eralice já pode aceder como administradora!'))