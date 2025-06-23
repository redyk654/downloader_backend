import yt_dlp

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title'),
            'duration': info.get('duration'),  # en secondes
            'quality': info.get('format'),
            'filesize': info.get('filesize') or 0,
            'url': info.get('url'),
            'ext': info.get('ext'),
        }

def download_video(info):
    """
    Simule un téléchargement et retourne le chemin final et la taille du fichier.
    En production, tu pourrais renvoyer une URL temporaire signée ou un fichier stocké.
    """
    # Ici on ne télécharge pas vraiment, on renvoie un lien simulé
    fake_path = f"https://cdn.monsite.com/telechargements/{info['title'].replace(' ', '_')}.{info['ext']}"
    return fake_path, info.get('filesize') or 0

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')
