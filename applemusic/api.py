import requests
import json
import re
import os
import sys
import time
import socket
from bs4 import BeautifulSoup

MAX_RETRIES = 3

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


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
    """Extrait les titres d'une playlist Apple Music publique (sans API key)."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(playlist_url, headers=_HEADERS, timeout=15)
            if response.status_code == 404:
                raise RuntimeError("Playlist introuvable — vérifiez l'URL.")
            if response.status_code == 403:
                raise RuntimeError("Accès refusé — la playlist est privée ou le lien a expiré.")
            response.raise_for_status()
            break
        except RuntimeError:
            raise
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"Impossible d'accéder à la page Apple Music : {e}")
            time.sleep(2)

    soup = BeautifulSoup(response.text, "html.parser")

    # Détection d'une page d'erreur Apple Music (playlist privée ou supprimée)
    title_tag = soup.find("title")
    page_title = title_tag.string.lower() if title_tag and title_tag.string else ""
    unavailable_keywords = ("not found", "page not found", "unavailable", "introuvable", "error")
    if any(k in page_title for k in unavailable_keywords):
        raise RuntimeError("Playlist introuvable ou privée — vérifiez que la playlist est bien publique.")

    # Méthode 1 — JSON-LD structuré (le plus fiable)
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if data.get("@type") == "MusicPlaylist":
                tracks = []
                for item in data.get("track", []):
                    name = item.get("name", "")
                    by_artist = item.get("byArtist", {})
                    if isinstance(by_artist, list):
                        artist = by_artist[0].get("name", "") if by_artist else ""
                    else:
                        artist = by_artist.get("name", "")
                    if name:
                        tracks.append(f"{name} {artist}".strip())
                if tracks:
                    return tracks
        except Exception:
            continue

    # Méthode 2 — Shoebox (données React embarquées dans le HTML)
    shoebox = soup.find("script", id=re.compile(r"shoebox-media-api-cache"))
    if shoebox and shoebox.string:
        try:
            data = json.loads(shoebox.string)
            tracks = []
            for key, value in data.items():
                try:
                    obj = json.loads(value) if isinstance(value, str) else value
                    for resource in obj.get("data", []):
                        if resource.get("type") == "songs":
                            attrs = resource.get("attributes", {})
                            name   = attrs.get("name", "")
                            artist = attrs.get("artistName", "")
                            if name:
                                tracks.append(f"{name} {artist}".strip())
                except Exception:
                    continue
            if tracks:
                return tracks
        except Exception:
            pass

    raise RuntimeError(
        "Aucun titre trouvé.\n"
        "Causes possibles :\n"
        "  • La playlist est privée (rendez-la publique dans Apple Music)\n"
        "  • L'URL n'est pas une playlist (vérifiez le lien)\n"
        "  • Apple Music a modifié la structure de sa page (contactez le développeur)"
    )
