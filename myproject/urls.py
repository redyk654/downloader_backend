from django.contrib import admin
from django.urls import path, include
from django_prometheus import exports # type: ignore

# Importe notre vue d'authentification personnalisée
from books.views import CustomAuthToken

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'), # URL pour l'authentification
    path('api/', include('books.urls')), # Inclut les URLs de notre application books
    path('', include('django_prometheus.urls')),
    # path('api/stats/', include
]
