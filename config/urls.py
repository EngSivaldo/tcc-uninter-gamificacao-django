from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 1. MUDANÇA: Importamos a 'index' (nosso porteiro) em vez da trail_list
from apps.gamification.views import index 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 2. CORREÇÃO CRÍTICA: A raiz agora chama a 'index'. 
    # Como a 'index' NÃO tem @login_required, ela vai abrir a Landing Page para visitantes.
    path('', index, name='home'),

    # Roteamento dos Apps
    path('gamification/', include('apps.gamification.urls')),
    path('accounts/', include('apps.accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.gamification.views.error_404'
handler500 = 'apps.gamification.views.error_500'