# Playlist Manager

Application Windows avec interface graphique pour télécharger et gérer des playlists musicales.

## Téléchargement

Dernière version : 
**[⬇ Télécharger PlaylistManager.exe](https://github.com/Yma061/deezer-youtube-mp3-downloader/releases/download/v1.1.0/PlaylistManager.exe)**

> Windows uniquement — aucune installation requise, double-cliquez pour lancer.

---

## Fonctionnalités

### 🎵 Deezer → YouTube
Importe une playlist Deezer dans ta bibliothèque YouTube automatiquement.
- Reprise automatique si la limite quotidienne de l'API est atteinte
- Limite : ~66 titres/jour (quota Google de 10 000 unités/jour)

### ▶ YouTube → MP3
Télécharge une playlist YouTube complète et convertit chaque vidéo en MP3 (192 kbps).
- Fichiers numérotés dans l'ordre de la playlist

### 📊 Excel → MP3
Télécharge des musiques dans l'ordre défini dans un fichier Excel.
- Pause aléatoire entre chaque titre pour éviter les blocages YouTube
- Fichier `non_trouves.txt` généré si des titres n'ont pas été trouvés

---

## Configuration Deezer → YouTube

Ce mode nécessite un fichier `client_secret.json` personnel :

1. Va sur [console.cloud.google.com](https://console.cloud.google.com)
2. Crée un projet et active l'**API YouTube Data v3**
3. Crée des identifiants **OAuth 2.0** (type : Application de bureau)
4. Télécharge le fichier JSON et sélectionne-le dans l'application

> Un guide complet est intégré directement dans l'application.

---

## Installation depuis les sources

```bash
pip install -r requirements.txt
python interface.py
```

## Technologies

Python · Tkinter · yt-dlp · Deezer API · YouTube Data API v3 · openpyxl · PyInstaller
