from rest_framework import viewsets # type: ignore
from rest_framework.response import Response
import yt_dlp
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import BookSerializer, DownloadOperationSerializer
from .models import DownloadOperation, Book

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


@api_view(['POST'])
def facebook_video_download(request):
    video_url = request.data.get('video_url')
    client_ip = request.META.get('REMOTE_ADDR')

    if not video_url:
        return Response({'error': 'Video URL is required'}, status=status.HTTP_400_BAD_REQUEST)

    DownloadOperation.objects.create(video_url=video_url, ip_address=client_ip)

    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            downloadable_url = info['url']
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'downloadable_url': downloadable_url}, status=status.HTTP_200_OK)

class DownloadOperationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DownloadOperation.objects.all().order_by('-timestamp')
    serializer_class = DownloadOperationSerializer