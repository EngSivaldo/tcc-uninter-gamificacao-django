import os
import re
from google import genai
from dotenv import load_dotenv
from pathlib import Path

# Configuração de Caminho: Localiza o .env na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

def gerar_conteudo_aula(titulo_aula):
    """
    Motor de Inteligência Artificial para geração de conteúdo educativo.
    Utiliza engenharia de prompt para garantir saída em HTML semântico.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "<p>❌ Erro de Configuração: GEMINI_API_KEY não encontrada no .env.</p>"

    client = genai.Client(api_key=api_key)
    
    # PROMPT ARQUITETÔNICO (Nível Super Sênior)
    prompt = f"""
    PERSONA: Atue como um Arquiteto de Soluções e Professor PhD em Engenharia de Software.
    OBJETIVO: Gerar uma aula técnica, profunda e visualmente estruturada sobre "{titulo_aula}".
    
    ESTRUTURA VISUAL OBRIGATÓRIA (USE ESTAS TAGS EXATAS):
    1. <h1>{titulo_aula}</h1> (Um parágrafo de impacto sobre a relevância do tema no mercado).
    2. <h2><i class="fas fa-exclamation-circle text-blue-500"></i> O Problema que resolvemos</h2>
       <p>(Descreva a dor do mercado ou o desafio técnico que este conceito endereça).</p>
    3. <h2><i class="fas fa-cogs text-blue-500"></i> Explicação Técnica Profunda</h2>
       <p>(Explique os fundamentos, arquitetura e funcionamento. Use <strong> para termos chave).</p>
    4. <h2><i class="fas fa-code text-blue-500"></i> Exemplo Prático (Mão na Massa)</h2>
       <p>Abaixo, um exemplo técnico de implementação:</p>
       <pre><code>(Insira aqui um código limpo em Python, Dockerfile ou YAML, devidamente comentado)</code></pre>
    5. <div class="my-10 p-6 bg-amber-50 border-l-8 border-amber-400 rounded-r-xl shadow-md">
         <h4 class="text-amber-800 font-black flex items-center gap-2 mb-2">
           <i class="fas fa-lightbulb"></i> DICA DE SUPER SÊNIOR
         </h4>
         <p class="text-amber-900 italic">(Forneça um insight de mercado sobre curadoria de dados, escalabilidade ou padrões de projeto relacionados ao tema).</p>
       </div>

    REGRAS TÉCNICAS RÍGIDAS:
    - Retorne APENAS o HTML interno (fragmento).
    - PROIBIDO incluir tags <html>, <head>, <body> ou declarações DOCTYPE.
    - PROIBIDO usar blocos de código markdown (```html).
    - PROIBIDO qualquer saudação ou texto introdutório. Comece diretamente no <h1>.
    - Linguagem: Português do Brasil, tom técnico e inspirador.
    """

    # Modelos disponíveis conforme seu teste de diagnóstico
    modelos_tentar = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']

    for modelo in modelos_tentar:
        try:
            print(f"DEBUG: Solicitando conteúdo ao modelo {modelo}...")
            response = client.models.generate_content(
                model=modelo,
                contents=prompt
            )
            
            if response and response.text:
                texto_bruto = response.text
                
                # --- SANITIZAÇÃO SÊNIOR (LIMPEZA DE RESÍDUOS) ---
                
                # 1. Remove marcações de bloco de código Markdown se a IA teimar em usá-las
                texto_limpo = re.sub(r'```html|```', '', texto_bruto)
                
                # 2. Corta qualquer texto (saudações) que venha antes do primeiro <h1>
                # Isso garante que a página comece limpa no título principal
                texto_limpo = re.sub(r'^.*?<h1', '<h1', texto_limpo, flags=re.DOTALL | re.IGNORECASE)
                
                print(f"✅ SUCESSO: Conteúdo gerado via {modelo} e sanitizado.")
                return texto_limpo.strip()
                
        except Exception as e:
            print(f"❌ FALHA no modelo {modelo}: {str(e)}")
            continue

    return "<p>❌ Falha Técnica: O sistema não conseguiu obter uma resposta válida da IA. Verifique sua cota no Google Cloud.</p>"