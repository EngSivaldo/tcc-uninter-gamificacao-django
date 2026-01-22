# Plataforma Gamificada de Estudos

Este projeto é uma aplicação web desenvolvida como Trabalho de Conclusão de Curso (TCC) para o curso de Engenharia de Software da UNINTER. A plataforma utiliza elementos de gamificação para incentivar o engajamento e a retenção de conhecimento por parte dos estudantes.

## 🚀 Tecnologias Utilizadas

- **Linguagem:** Python 3.13
- **Framework Web:** Django
- **Base de Dados:** PostgreSQL
- **Estilização:** Tailwind CSS
- **Infraestrutura:** Docker & Docker Compose

## 🛠️ Modos de Execução

O projeto foi configurado para ser executado de duas formas, garantindo portabilidade e eficiência.

### 1. Execução Local (Modo venv)

Ideal para desenvolvimento rápido e máquinas com recursos limitados.

**Pré-requisitos:** Python 3.13 e PostgreSQL instalados localmente.

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/EngSivaldo/tcc-uninter-gamificacao-django.git]
    (https://github.com/EngSivaldo/tcc-uninter-gamificacao-django.git)
    ```
2.  Crie e ative o ambiente virtual:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure as variáveis de ambiente no ficheiro `.env` (conforme o ficheiro `.env.example`).
5.  Execute as migrações e inicie o servidor:
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

### 2. Execução via Docker

Ideal para demonstração e ambientes de produção.

**Pré-requisitos:** Docker e Docker Compose instalados.

1.  Na raiz do projeto, execute:
    ```bash
    docker-compose up --build
    ```
2.  O sistema estará disponível em `http://localhost:8000`.

## ⚙️ Variáveis de Ambiente

O projeto utiliza um ficheiro `.env` para gerir configurações sensíveis:

- `SECRET_KEY`: Chave de segurança do Django.
- `DEBUG`: Define o modo de depuração (True/False).
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Credenciais da base de dados.

## 👥 Autores

- **Sivaldo Vieira de Almeida** (RU: 4139872)
- **Eralice de Moraes Baía** (RU: 4144099)

---

_Projeto desenvolvido para a disciplina de Estágio Supervisionado / TCC - UNINTER 2026._
