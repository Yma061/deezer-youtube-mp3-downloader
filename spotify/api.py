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
    """Retourne la liste 'Titre Artiste' d'une playlist Spotify publique."""
    from spotdl.utils.spotify import SpotifyClient
    from spotdl.types.song import Song

    # spotdl embarque ses propres credentials — aucun compte développeur requis
    try:
        SpotifyClient.init(
            client_id="5f573c9620494bae87890c0f08a60293",
            client_secret="212476d9b0f3472eaa762d90b19b0ba8",
        )
    except Exception:
        pass  # déjà initialisé

    songs = Song.list_from_url(playlist_url)
    return [f"{s.name} {s.artists[0]}" for s in songs]


def download_playlist(playlist_url, output_folder="playlists", on_progress=None):
    """Télécharge une playlist Spotify en MP3 via spotdl."""
    from spotdl import Spotdl

    os.makedirs(output_folder, exist_ok=True)

    extra = {"ffmpeg": _ffmpeg_path()} if _ffmpeg_path() else {}

    app = Spotdl(
        client_id="5f573c9620494bae87890c0f08a60293",
        client_secret="212476d9b0f3472eaa762d90b19b0ba8",
        downloader_settings={
            "output": os.path.join(output_folder, "{list-name}/{list-position} - {title} - {artists}"),
            "format": "mp3",
            "bitrate": "192k",
            "overwrite": "skip",
            **extra,
        },
    )

    print("Récupération des titres Spotify...")
    songs = app.search([playlist_url])
    total = len(songs)
    print(f"{total} titres trouvés.")

    for i, song in enumerate(songs, start=1):
        print(f"[{i}/{total}] {song.name} — {song.artists[0]}")
        if on_progress:
            on_progress(i - 1, total, f"{song.name} — {song.artists[0]}")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                _, _ = app.download(song)
                break
            except Exception as e:
                err = str(e).lower()
                if any(k in err for k in ("timed out", "connection", "network")):
                    wait_for_connection()
                if attempt < MAX_RETRIES:
                    print(f"  Tentative {attempt}/{MAX_RETRIES} échouée, nouvel essai...")
                    time.sleep(3)
                else:
                    print(f"  ERREUR : {e}")

        if on_progress:
            on_progress(i, total, f"{song.name} — {song.artists[0]}")
