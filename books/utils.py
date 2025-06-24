# utils.py
import yt_dlp
import re


def extract_video_metadata(video_url: str, format_preference: str = 'best'):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': format_preference,
        'noplaylist': True,
        'forcejson': True,
        'extract_flat': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=False)
            direct_url = info_dict.get('url')
            video_format = sanitize_format(info_dict.get('format_note'))
            duration = info_dict.get('duration')
            filesize = info_dict.get('filesize') or info_dict.get('filesize_approx')

            return {
                'direct_url': direct_url,
                'format': video_format,
                'duration': duration,
                'filesize': filesize,
            }
        except yt_dlp.utils.DownloadError as e:
            raise Exception(f"Erreur yt_dlp : {str(e)}")


def sanitize_format(format_note):
    if not format_note:
        return "unknown"
    match = re.match(r"^(\d{3,4})p", format_note.strip())
    return match.group(0) if match else "unknown"


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')
