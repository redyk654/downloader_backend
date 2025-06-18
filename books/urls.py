from django.urls import path
from .views import (
    DownloadStatCreateAPIView,
    DownloadStatsOverviewAPIView,
    DownloadStatsTimeSeriesAPIView,
    DownloadStatsByQualityAPIView,
    DownloadStatsByCountryAPIView,
)

urlpatterns = [
    # Endpoint pour enregistrer un téléchargement (public)
    path('downloads/record/', DownloadStatCreateAPIView.as_view(), name='record_download'),

    # Endpoints pour les statistiques (protégés par authentification)
    path('stats/overview/', DownloadStatsOverviewAPIView.as_view(), name='stats_overview'),
    path('stats/timeseries/', DownloadStatsTimeSeriesAPIView.as_view(), name='stats_timeseries'),
    path('stats/by-quality/', DownloadStatsByQualityAPIView.as_view(), name='stats_by_quality'),
    path('stats/by-country/', DownloadStatsByCountryAPIView.as_view(), name='stats_by_country'),
]
# router = DefaultRouter()
# router.register(r'download-operations', DownloadOperationViewSet)

# urlpatterns = [
#     path('facebook-download/', facebook_video_download, name='facebook-download'),
#     path('', include(router.urls)),
# ]