import os
import re
import json
import time
from django.core.management.base import BaseCommand
from google import genai
from apps.gamification.models import Chapter, Questao, Alternativa

class Command(BaseCommand):
    help = 'Gera questões automáticas usando estratégia de fallback para evitar erro 429'

    def add_arguments(self, parser):
        parser.add_argument('chapter_id', type=int, help='ID do capítulo para o qual gerar questões')

    def handle(self, *args, **options):
        chapter_id = options['chapter_id']
        
        # 1. Busca o Capítulo
        try:
            chapter = Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Capítulo {chapter_id} não encontrado.'))
            return

        if not chapter.content:
            self.stdout.write(self.style.WARNING(f'⚠️ O capítulo "{chapter.title}" não possui conteúdo para basear as questões.'))
            return

        # 2. Configura o Cliente
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.stdout.write(self.style.ERROR("❌ GEMINI_API_KEY não encontrada no arquivo .env"))
            return
            
        client = genai.Client(api_key=api_key)
        
        # 3. Prompt Refinado
        prompt = f"""
        OBJETIVO: Gerar 3 questões de múltipla escolha sobre o conteúdo técnico abaixo.
        CONTEÚDO: "{chapter.content}"
        
        REGRAS RÍGIDAS:
        1. Retorne APENAS um JSON puro (Array).
        2. Cada questão deve ter 4 alternativas.
        3. Apenas uma 'correta': true.
        4. XP padrão: 10.

        FORMATO OBRIGATÓRIO:
        [
          {{
            "enunciado": "Pergunta?",
            "xp": 10,
            "alternativas": [
              {{"texto": "Opção A", "correta": true}},
              {{"texto": "Opção B", "correta": false}},
              {{"texto": "Opção C", "correta": false}},
              {{"texto": "Opção D", "correta": false}}
            ]
          }}
        ]
        """

        # 4. Ciclo de Tentativas com Fallback
        modelos_tentar = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']
        sucesso = False

        for modelo in modelos_tentar:
            try:
                self.stdout.write(f"DEBUG: Solicitando Quiz ao modelo {modelo}...")
                response = client.models.generate_content(
                    model=modelo,
                    contents=prompt
                )
                
                if response and response.text:
                    # SANITIZAÇÃO (Remove blocos de código markdown)
                    texto_limpo = re.sub(r'```json|```|json', '', response.text).strip()
                    questoes_data = json.loads(texto_limpo)

                    # 5. Salva no Banco de Dados
                    for item in questoes_data:
                        q = Questao.objects.create(
                            chapter=chapter,
                            enunciado=item['enunciado'],
                            xp_recompensa=item.get('xp', 10)
                        )
                        for alt in item['alternativas']:
                            Alternativa.objects.create(
                                questao=q,
                                texto=alt['texto'],
                                e_correta=alt['correta']
                            )
                    
                    self.stdout.write(self.style.SUCCESS(f"✅ SUCESSO: Questões geradas e salvas via {modelo}"))
                    sucesso = True
                    break 

            except Exception as e:
                erro_str = str(e)
                self.stdout.write(self.style.WARNING(f"⚠️ FALHA no modelo {modelo}: {erro_str}"))
                
                # Se for erro de cota (429), espera um pouco antes de tentar o próximo modelo
                if "429" in erro_str or "RESOURCE_EXHAUSTED" in erro_str:
                    self.stdout.write("Aguardando 5 segundos para renovação de cota...")
                    time.sleep(5)
                continue

        if not sucesso:
            self.stdout.write(self.style.ERROR("❌ Falha crítica: Nenhum modelo conseguiu processar o pedido."))