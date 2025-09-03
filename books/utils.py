# utils.py
import yt_dlp
import re, logging

logger = logging.getLogger(__name__)

def get_available_resolutions(video_url):
    """
    Retourne la liste des résolutions disponibles pour une vidéo.
    Exemple : ['144p', '360p', '720p']
    """
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'socket_timeout': 10,
        'format': 'bestvideo*+bestaudio/best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        formats = info.get("formats", [])
        resolutions = set()

        for fmt in formats:
            height = fmt.get("height")
            note = fmt.get("format_note") or (f"{height}p" if height else "")
            cleaned = sanitize_format(note)
            if cleaned != "unknown":
                resolutions.add(cleaned)

        return sorted(resolutions, key=lambda x: int(x.replace("p", "")))  # tri croissant

    except Exception as e:
        logger.error(f"Erreur yt_dlp: {str(e)}")
        raise RuntimeError("Impossible d’extraire les formats disponibles.")


def extract_video_metadata(video_url: str, format_preference: str = 'worst'):
    """
    Extracts video metadata and returns a dict with the info.
    Raises a custom error message in English depending on platform and error type.
    """
    if not video_url:
        raise ValueError("Video URL cannot be empty.")

    def detect_platform(url):
        url = url.lower()
        if "twitter.com" in url or "x.com" in url:
            return "Twitter"
        if "tiktok.com" in url:
            return "TikTok"
        if "instagram.com" in url:
            return "Instagram"
        if "facebook.com" in url or "fb.watch" in url:
            return "Facebook"
        if "youtube.com" in url or "youtu.be" in url:
            return "YouTube"
        return "Other"

    platform = detect_platform(video_url)

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': format_preference,
        'noplaylist': True,
        'forcejson': True,
        'extract_flat': False,
        'extractor_args': {
            'tiktok': {
                'app_version': '29.9.9',
                'manifest_app_version': '299900',
                'version_code': '299900',
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
            'Origin': 'https://www.tiktok.com',
            'Authority': 'www.tiktok.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'TE': 'trailers',
        },
        'socket_timeout': 30,
        'source_address': '0.0.0.0',
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
            err_str = str(e)
            # Custom error messages in English
            if platform == "Twitter":
                if "NsfwViewerHasNoStatedAge" in err_str:
                    raise Exception("This tweet contains sensitive (NSFW) content and cannot be downloaded without authentication.")
                if "Requested tweet is unavailable" in err_str:
                    raise Exception("The requested tweet is unavailable or private.")
                raise Exception("Unable to download Twitter video. Please check that the tweet is public and accessible.")
            elif platform == "TikTok":
                if "Video unavailable" in err_str or "Private video" in err_str:
                    raise Exception("The TikTok video is private or unavailable.")
                raise Exception("Unable to download TikTok video. Please check the link.")
            elif platform == "Instagram":
                if "login required" in err_str:
                    raise Exception("Instagram video requires login to download.")
                raise Exception("Unable to download Instagram video. Please check the link.")
            elif platform == "Facebook":
                if "login required" in err_str:
                    raise Exception("Facebook video requires login to download.")
                raise Exception("Unable to download Facebook video. Please check the link.")
            elif platform == "YouTube":
                raise Exception("YouTube downloading is not supported on this platform.")
            else:
                raise Exception("Error extracting video. Please check the link or platform.")
        except Exception as e:
            raise Exception(f"Unexpected error while extracting video metadata: {str(e)}")


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


def build_yt_dlp_format(format_str: str) -> str:
    """
    Convertit un format simple (ex: '360p') en syntaxe yt-dlp.
    Exemples :
        '360p' -> 'bestvideo[height=360]+bestaudio/best[height=360]'
        '720p' -> 'bestvideo[height=720]+bestaudio/best[height=720]'
        'best' -> 'best'
        'worst' -> 'worst'
    """
    if format_str in ('best', 'worst'):
        return format_str
    if format_str.endswith('p') and format_str[:-1].isdigit():
        height = format_str[:-1]
        return f'bestvideo[height={height}]+bestaudio/best[height={height}]'
    # fallback: retourne le format tel quel
    return format_str
