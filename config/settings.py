import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 1. Configuração de Caminhos (BASE_DIR)
# BASE_DIR aponta para a raiz do projeto (onde está o manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Carregamento de Variáveis de Ambiente
# Forçamos o caminho absoluto para o .env para evitar erros de leitura
load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)


# 3. Ajuste do Path para a pasta 'apps'
# Isso permite importar como 'accounts' em vez de 'apps.accounts' se desejar,
# mas mantém a compatibilidade com sua estrutura atual.
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# 4. Segurança e Core
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-change-me')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
# Se o DEBUG for False, precisamos dizer quais domínios podem acessar o site
# Em desenvolvimento/Docker, usamos '*' ou 'localhost 127.0.0.1'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost 127.0.0.1').split()

# 5. Definição de Aplicativos
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Bibliotecas de Terceiros
    'django_extensions',
    
    # Seus Apps Customizados (na pasta /apps)
    'apps.accounts',
    'apps.gamification',
]

# 6. Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # DEVE
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# 7. Configuração de Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# 8. Banco de Dados (Híbrido e Resiliente)
import dj_database_url

# Tentamos carregar a DATABASE_URL (comum em servidores como Render/Heroku)
database_url = os.getenv('DATABASE_URL')

if database_url:
    DATABASES = {
        'default': dj_database_url.config(default=database_url, conn_max_age=600)
    }
else:
    # Se não houver DATABASE_URL, tentamos as variáveis separadas
    # Se o nome do banco não existir no .env, usamos o SQLite como última salvação
    db_name = os.getenv('DB_NAME')
    
    if db_name:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': db_name,
                'USER': os.getenv('DB_USER', 'postgres'),
                'PASSWORD': os.getenv('DB_PASSWORD', ''),
                'HOST': os.getenv('DB_HOST', '127.0.0.1'),
                'PORT': os.getenv('DB_PORT', '5432'),
            }
        }
    else:
        # SALVA-VIDAS: Se nada for configurado, o projeto abre em SQLite
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

# 9. Autenticação Customizada (Importante para o TCC)
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 10. Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# 11. Arquivos Estáticos e Media
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Otimização para o WhiteNoise servir arquivos compactados
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 12. Rotas de Login/Redirecionamento
LOGIN_URL = 'accounts:login'

# O aluno loga e cai no "Porteiro Inteligente" (gamification:index)
# que decide se mostra o 'home.html' (Continuar Estudando)
LOGIN_REDIRECT_URL = 'gamification:index'

# Ao sair, ele volta para a raiz, onde verá a sua Landing Page de vendas
LOGOUT_REDIRECT_URL = 'gamification:index'

# 13. Configurações de Campo Padrão
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True