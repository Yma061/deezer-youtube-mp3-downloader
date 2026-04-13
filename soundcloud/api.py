import yt_dlp
import os
import sys
import time
import socket

MAX_RETRIES = 3


def _ffmpeg_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return None


def is_connected():
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except Exception:
        return False


def wait_for_connection(print_fn=print):
    if is_connected():
        return
    print_fn("  Connexion perdue — attente du retour internet...")
    while not is_connected():
        time.sleep(5)
    print_fn("  Connexion rétablie, reprise.")


def get_tracks(playlist_url):
    """Retourne la liste 'Titre Artiste' d'une playlist SoundCloud publique."""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        tracks = []
        for entry in (info.get('entries') or []):
            title    = entry.get('title', '')
            uploader = entry.get('uploader', '')
            if title:
                tracks.append(f"{title} {uploader}".strip())
        return tracks


def download_playlist(playlist_url, output_folder='playlists', on_progress=None):
    """Télécharge une playlist SoundCloud en MP3 via yt-dlp."""
    counter = {"done": 0, "total": 0}

    def progress_hook(d):
        if d["status"] == "finished":
            info = d.get("info_dict", {})
            counter["total"] = info.get("playlist_count") or counter["total"]
            counter["done"] += 1
            title = info.get("title", "")
            if on_progress:
                on_progress(counter["done"], counter["total"], title)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': {
            'default': os.path.join(
                output_folder,
                '%(playlist_title)s',
                '%(playlist_index)s - %(title)s - %(uploader)s.%(ext)s'
            ),
        },
        'nooverwrites': True,
        'socket_timeout': 20,
        'progress_hooks': [progress_hook],
        **({'ffmpeg_location': _ffmpeg_path()} if _ffmpeg_path() else {}),
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("Lancement du téléchargement...")
                ydl.download([playlist_url])
                print("\nOpération terminée avec succès !")
            return
        except Exception as e:
            err = str(e).lower()
            if any(k in err for k in ("timed out", "connection", "network", "read timed")):
                wait_for_connection()
            if attempt < MAX_RETRIES:
                print(f"Tentative {attempt}/{MAX_RETRIES} échouée, nouvel essai...")
                time.sleep(3)
            else:
                print(f"\nERREUR après {MAX_RETRIES} tentatives : {e}")
