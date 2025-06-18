from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import facebook_video_download, DownloadOperationViewSet

router = DefaultRouter()
router.register(r'download-operations', DownloadOperationViewSet)

urlpatterns = [
    path('facebook-download/', facebook_video_download, name='facebook-download'),
    path('', include(router.urls)),
]