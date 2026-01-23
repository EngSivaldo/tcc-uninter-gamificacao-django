from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
# Importamos a view da vitrine para usá-la como Home Page
from apps.gamification.views import trail_list

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rota Raiz: Agora aponta diretamente para a vitrine de cursos (Estilo Coursera)
    path('', trail_list, name='home'),

    # Roteamento dos Apps
    path('accounts/', include('apps.accounts.urls')),
    path('gamification/', include('apps.gamification.urls')),
]

# Servir arquivos de mídia em ambiente de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Handlers de Erro (Ajustados para o app gamification)
handler404 = 'apps.gamification.views.error_404'
handler500 = 'apps.gamification.views.error_500'