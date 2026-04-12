# Playlist Manager

Application Python avec interface graphique permettant de gérer et télécharger des playlists musicales via trois modes.

## Fonctionnalités

### Deezer → YouTube
Importe une playlist Deezer dans ta bibliothèque YouTube automatiquement.
- Reprise automatique si la limite quotidienne de l'API est atteinte
- Limite : ~66 titres/jour (quota Google de 10 000 unités/jour)

### YouTube → MP3
Télécharge une playlist YouTube complète et convertit chaque vidéo en MP3 (192 kbps).
- Fichiers numérotés dans l'ordre de la playlist

### Excel → MP3
Télécharge des musiques dans l'ordre défini dans un fichier Excel.
- Colonne E, feuille "Deezer"
- Pause aléatoire entre chaque titre pour éviter les blocages YouTube
- Fichier `non_trouves.txt` généré si des titres n'ont pas été trouvés

---

## Utilisation (.exe)

1. Télécharge `PlaylistManager.exe` depuis les [Releases](../../releases)
2. Lance le fichier — aucune installation requise
3. Choisis un mode et suis les instructions à l'écran

---

## Installation (depuis les sources)

### Prérequis

- Python 3.10+
- FFmpeg installé et accessible dans le PATH

### Dépendances

```bash
pip install -r requirements.txt
```

### Lancement

```bash
python interface.py
```

---

## Configuration Deezer → YouTube

Ce mode nécessite un fichier `client_secret.json` personnel :

1. Va sur [console.cloud.google.com](https://console.cloud.google.com)
2. Crée un projet et active l'**API YouTube Data v3**
3. Crée des identifiants **OAuth 2.0** (type : Application de bureau)
4. Télécharge le fichier JSON et sélectionne-le dans l'application

> Ne partage jamais ton `client_secret.json` — il est lié à ton compte Google.

---

## Structure du projet

```
playlist/
├── interface.py            # Application principale (GUI)
├── deezer.py               # Récupération playlist Deezer
├── youtube.py              # Import vers YouTube
├── youtube_to_mp3.py       # Téléchargement playlist YouTube
├── download_from_excel.py  # Téléchargement depuis Excel
└── requirements.txt        # Dépendances Python
```

## Technologies

- Python / Tkinter
- yt-dlp
- Deezer API
- YouTube Data API v3 / OAuth 2.0
- openpyxl
- PyInstaller
