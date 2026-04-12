import yt_dlp
import os
import re
import sys

def _ffmpeg_path():
    """Retourne le dossier contenant ffmpeg (fonctionne en .exe et en script)."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return None

def sanitize_filename(filename):
    """
    Nettoie une chaîne de caractères pour qu'elle puisse être utilisée comme nom de fichier.
    Supprime les caractères invalides et les remplace par un underscore.
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_and_convert_playlist(playlist_url, output_folder='playlists', on_progress=None):
    """
    Télécharge une playlist YouTube, convertit chaque vidéo en MP3 et l'organise
    dans un dossier portant le nom de la playlist.

    Args:
        playlist_url (str): L'URL de la playlist YouTube.
        output_folder (str): Le dossier parent où les playlists seront sauvegardées.
    """
    print(f"Traitement de la playlist : {playlist_url}")

    counter = {"done": 0, "total": 0}

    def progress_hook(d):
        if d["status"] == "finished":
            info = d.get("info_dict", {})
            counter["total"] = info.get("playlist_count") or counter["total"]
            counter["done"] += 1
            title = info.get("title", "")
            if on_progress:
                on_progress(counter["done"], counter["total"], title)

    # --- Configuration pour yt-dlp ---
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': {
            'default': os.path.join(output_folder, '%(playlist_title)s', '%(playlist_index)s - %(title)s - %(uploader)s.%(ext)s'),
        },
        'nooverwrites': True,
        'continue_dl': True,
        'progress_hooks': [progress_hook],
        **({'ffmpeg_location': _ffmpeg_path()} if _ffmpeg_path() else {}),
    }

    try:
        # On crée une instance de YoutubeDL avec nos options
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # On lance le processus de téléchargement pour la playlist
            print("Lancement du téléchargement et de la conversion...")
            ydl.download([playlist_url])
            print("\nOpération terminée avec succès !")
            print(f"Les fichiers ont été sauvegardés dans un sous-dossier de '{output_folder}'.")

    except yt_dlp.utils.DownloadError as e:
        print(f"\nERREUR : Une erreur de téléchargement est survenue : {e}")
        print("Vérifie que l'URL de la playlist est correcte et que la playlist est publique.")
    except Exception as e:
        print(f"\nERREUR : Une erreur inattendue est survenue : {e}")

# --- Point d'entrée du programme ---
if __name__ == "__main__":
    # Remplace cette URL par l'URL de la playlist YouTube que tu veux télécharger.
    # Exemple : "https://www.youtube.com/playlist?list=PL4o29bINVT4EG_y-k5jGoOu3-Am8Nvi10"
    playlist_url_input = input("Veuillez entrer l'URL de la playlist YouTube : ")

    if playlist_url_input:
        # On appelle la fonction principale avec l'URL fournie par l'utilisateur
        download_and_convert_playlist(playlist_url_input)
    else:
        print("Aucune URL fournie. Le programme va se fermer.")