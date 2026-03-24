import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# 1. Configuração de Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Carregamento de Variáveis de Ambiente
load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)

# 3. Ajuste do Path para a pasta 'apps'
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# 4. Segurança e Core
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-change-me')

# CORREÇÃO CRÍTICA: Garantir que o Django entenda o booleano True
DEBUG = os.getenv('DEBUG', 'False').strip().upper() == 'TRUE'

# Adicionamos '*' para evitar o Erro 400 enquanto você configura o PC novo
# ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '172.29.42.229', '0.0.0.0', '*']
# No seu settings.py (no VS Code)
ALLOWED_HOSTS = ['tcc-uninter-gamificacao-django.onrender.com', '127.0.0.1', 'localhost']

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
    
    # Seus Apps Customizados
    'apps.accounts',
    'apps.gamification',
]

# 6. Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
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

# 8. Banco de Dados
database_url = os.getenv('DATABASE_URL')

if database_url:
    DATABASES = {
        'default': dj_database_url.config(default=database_url, conn_max_age=600)
    }
else:
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
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

# 9. Autenticação
AUTH_USER_MODEL = 'accounts.User'

# 10. Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# 11. Arquivos Estáticos
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 12. Login/Redirecionamento
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'gamification:index'
LOGOUT_REDIRECT_URL = 'gamification:index'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURAÇÃO DE SEGURANÇA (O CORAÇÃO DO PROBLEMA) ---
# Só ativa o HTTPS se o DEBUG for False (Produção no Render)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # Garante que em desenvolvimento o HTTPS nunca seja forçado
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False