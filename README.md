# Playlist Manager

Application Windows avec interface graphique pour télécharger et gérer des playlists musicales.

## Téléchargement

Dernière version : **v1.1.0**  
**[⬇ Télécharger PlaylistManager.exe](https://github.com/Yma061/deezer-youtube-mp3-downloader/releases/download/v1.1.0/PlaylistManager.exe)**

> Windows uniquement — aucune installation requise, double-cliquez pour lancer.

### ⚠️ Avertissement Windows au premier lancement

Windows peut afficher un message de sécurité car le fichier n'est pas signé par un éditeur certifié. C'est normal pour une application indépendante.

**Pour lancer l'application :**

1. Clique sur **"Informations complémentaires"**

   ![SmartScreen étape 1](docs/smartscreen_1.png)

2. Clique sur **"Exécuter quand même"**

   ![SmartScreen étape 2](docs/smartscreen_2.png)

> Le fichier est open source — tu peux inspecter l'intégralité du code dans ce dépôt.

---

## Fonctionnalités

### 🎵 Deezer → YouTube
Importe une playlist Deezer dans ta bibliothèque YouTube automatiquement.
- Connexion Google intégrée — une fenêtre s'ouvre dans le navigateur au premier lancement, la connexion est mémorisée ensuite
- Reprise automatique si la limite quotidienne de l'API est atteinte
- Limite : ~66 titres/jour (quota Google de 10 000 unités/jour)

### ▶ YouTube → MP3
Télécharge une playlist YouTube complète et convertit chaque vidéo en MP3 (192 kbps).
- Fichiers numérotés dans l'ordre de la playlist

### 📊 Excel → MP3
Télécharge des musiques dans l'ordre défini dans un fichier Excel.
- Détection automatique des feuilles, choix de la colonne et de la ligne de départ
- Pause aléatoire entre chaque titre pour éviter les blocages YouTube
- Fichier `non_trouves.txt` généré si des titres n'ont pas été trouvés
- Bouton "Réessayer les titres manquants" pour relancer uniquement les échecs

---

## Interface

- Thème clair / sombre
- Barre de progression avec estimation du temps restant (ETA)
- Historique des 5 derniers téléchargements sur la page d'accueil
- Ouverture du dossier de sortie en un clic
- Notification sonore à la fin de chaque traitement

---

## Utilisation

### Deezer → YouTube
1. Lance l'application
2. Clique sur **Deezer → YouTube**
3. Entre l'ID de ta playlist Deezer (le nombre à la fin de l'URL)
4. Clique sur **Lancer** — une fenêtre de connexion Google s'ouvre au premier lancement
5. La connexion est mémorisée pour les prochaines fois

### YouTube → MP3
1. Clique sur **YouTube → MP3**
2. Colle l'URL de la playlist YouTube
3. Clique sur **Lancer** — les MP3 sont sauvegardés dans `playlists/`

### Excel → MP3
1. Clique sur **Excel → MP3**
2. Sélectionne ton fichier Excel via **Parcourir...**
3. Choisis la feuille, la colonne et la première ligne de données
4. Entre un nom de playlist et clique sur **Lancer**

---

## Installation depuis les sources

```bash
pip install -r requirements.txt
python interface.py
```

### Build .exe

```bash
pyinstaller PlaylistManager.spec
```

---

## Technologies

Python · Tkinter · yt-dlp · Deezer API · YouTube Data API v3 · openpyxl · keyring · PyInstaller
