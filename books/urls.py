from django.urls import path
from .views import get_formats_video
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

    # Endpoint pour les obtenir les formats disponibles (public)
    path('downloads/formats/', get_formats_video, name='get_formats_videos'),

    # Endpoints pour les statistiques (protégés par authentification)
    path('stats/overview/', DownloadStatsOverviewAPIView.as_view(), name='stats_overview'),
    path('stats/timeseries/', DownloadStatsTimeSeriesAPIView.as_view(), name='stats_timeseries'),
    path('stats/by-quality/', DownloadStatsByQualityAPIView.as_view(), name='stats_by_quality'),
    path('stats/by-country/', DownloadStatsByCountryAPIView.as_view(), name='stats_by_country'),
]