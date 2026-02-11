# 🎓 Plataforma Gamificada de Estudos (TCC)

Esta plataforma é um ecossistema educacional desenvolvido como Trabalho de Conclusão de Curso (TCC) para o curso de Engenharia de Software da **UNINTER**. O sistema utiliza **Gamificação** e **Inteligência Artificial (Google Gemini)** para automatizar a criação de conteúdos didáticos e questionários, promovendo uma experiência de aprendizado dinâmica e engajadora.

## 🚀 Diferenciais Técnicos

- **IA Generativa Integrada:** Geração automática de textos de aula e questionários de múltipla escolha via API do Google Gemini.
- **Arquitetura Resiliente:** Suporte híbrido configurado para PostgreSQL (Produção/Docker) e SQLite (Desenvolvimento/Clone rápido) via `dj_database_url`.
- **CLI de Automação:** Comandos customizados (Management Commands) para sincronização de usuários e carga massiva de dados iniciais.
- **Segurança:** Gestão de ambiente via variáveis segregadas em arquivos `.env`.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.13
- **Framework Web:** Django 5.x
- **IA:** Google GenAI SDK (Gemini 2.0/1.5 Flash)
- **Banco de Dados:** PostgreSQL & SQLite
- **Estilização:** Tailwind CSS & Flowbite
- **Infraestrutura:** Docker, Docker Compose & WhiteNoise

---

## 💻 Guia de Instalação Rápida (Modo venv)

Siga os passos abaixo para clonar e rodar o projeto localmente:

### 1. Clonagem e Ambiente Virtual

```powershell
# Clone o repositório
git clone [https://github.com/EngSivaldo/tcc-uninter-gamificacao-django.git](https://github.com/EngSivaldo/tcc-uninter-gamificacao-django.git)
cd tcc-uninter-gamificacao-django

# Crie e ative o ambiente virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

2. Configuração das Variáveis de Ambiente
   Crie um arquivo chamado .env na raiz do projeto (onde reside o manage.py) e utilize o conteúdo do .env.example como base:

Ini, TOML
SECRET_KEY=sua-chave-secreta
DEBUG=True
GEMINI_API_KEY=sua_chave_do_google_ai_studio
DATABASE_URL=postgres://postgres:senha@127.0.0.1:5432/nome_do_banco

3. Automação de Carga e Inicialização
   Execute a sequência de comandos abaixo para preparar o banco e popular os dados iniciais automaticamente:

# 1. Executa as migrações (cria as tabelas)

python manage.py migrate

# 2. Popula Usuários (Sivaldo/Eralice), Trilhas, Capítulos e Medalhas

python manage.py seed_data

# 3. (Opcional) Gera questões via IA para o capítulo de ID 1

python manage.py gerar_questoes 1

# 4. Inicia o servidor

python manage.py runserver

Execução via Docker
Para rodar o projeto em containers isolados:
O sistema estará disponível em: http://localhost:8000

Bash
docker-compose up --build

Variável,Descrição,Valor Sugerido
DATABASE_URL,String de conexão do banco,postgres://... ou vazio para SQLite
GEMINI_API_KEY,Chave da API do Google,Obter no Google AI Studio
DEBUG,Modo de depuração,True em desenvolvimento
SECRET_KEY,Chave de segurança Django,Uma string longa e aleatória

Utilizando a IA no Painel Administrativo
O projeto conta com ferramentas de IA diretamente no Django Admin:

Acesse /admin com as credenciais criadas pelo seed_data (Login: sivaldo / Senha: uninter123).

Navegue até Capítulos.

Selecione os itens desejados na lista.

No menu de "Ações", selecione: "🤖 1. Gerar Texto da Aula via IA" ou "📝 2. Gerar Questionário via IA".

Autores
Sivaldo Vieira de Almeida (RU: 4139872)

Eralice de Moraes Baía (RU: 4144099)

Projeto desenvolvido para a disciplina de Estágio Supervisionado / TCC - UNINTER 2026.

Para finalizar o processo, execute o commit conforme o seu padrão:
`git add README.md`
`git commit -m 'pronto'`
