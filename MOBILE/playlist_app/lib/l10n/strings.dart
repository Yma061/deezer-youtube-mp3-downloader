const Map<String, Map<String, dynamic>> kStrings = {
  'fr': {
    'app_title':        'Playlist Manager',
    'choose_action':    'Choisissez une action',
    'choose_platform':  'Choisissez votre plateforme',
    'back':             'Retour',
    'launch':           'Lancer',
    'theme_dark':       'Thème sombre',
    'theme_light':      'Thème clair',
    'lang_btn':         '🇬🇧 EN',
    'what_it_does':     'Ce que ça fait',
    'what_you_need':    'Ce dont vous avez besoin',
    'open_folder':      'Ouvrir le dossier',
    'recent_dl':        'Téléchargements récents',

    // Cartes accueil
    'card_streaming_title': 'Streaming  →  YouTube',
    'card_streaming_desc':  'Importe une playlist Deezer ou Spotify\ndans ta bibliothèque YouTube',
    'card_youtube_title':   'YouTube  →  MP3',
    'card_youtube_desc':    'Télécharge une playlist YouTube\net convertit chaque vidéo en MP3',
    'card_excel_title':     'Excel  →  MP3',
    'card_excel_desc':      'Télécharge les musiques dans\nl\'ordre défini dans un fichier Excel',

    // Cartes streaming
    'card_deezer_title':      'Deezer  →  YouTube',
    'card_deezer_desc':       'Importe une playlist Deezer\ndans ta bibliothèque YouTube',
    'card_spotify_title':     'Spotify  →  YouTube',
    'card_spotify_desc':      'Importe une playlist Spotify\ndans ta bibliothèque YouTube',
    'card_soundcloud_title':  'SoundCloud  →  YouTube',
    'card_soundcloud_desc':   'Importe une playlist SoundCloud\ndans ta bibliothèque YouTube',
    'card_apple_title':       'Apple Music  →  YouTube',
    'card_apple_desc':        'Importe une playlist Apple Music\ndans ta bibliothèque YouTube',

    // Deezer
    'deezer_what': 'Récupère tous les titres d\'une playlist Deezer et les importe automatiquement dans une nouvelle playlist YouTube sur ton compte Google.',
    'deezer_needs': [
      'L\'ID de ta playlist Deezer  (ex : 14838804003)',
      'Une connexion internet',
      'Au premier lancement : connexion à ton compte Google dans le navigateur',
      '✅  Connexion mémorisée — tu n\'auras à te connecter qu\'une seule fois.',
      '⚠  Limite YouTube : 10 000 unités/jour — chaque titre coûte 150 unités.',
      '✅  Reprise automatique : relancez avec le même ID.',
    ],
    'deezer_input_label':       'ID de la playlist Deezer',
    'deezer_input_placeholder': 'ex : 14838804003',

    // Spotify
    'spotify_what': 'Récupère tous les titres d\'une playlist Spotify et les importe automatiquement dans une nouvelle playlist YouTube sur ton compte Google.',
    'spotify_needs': [
      'L\'URL de ta playlist Spotify',
      'La playlist doit être publique',
      'Une connexion internet',
      '✅  Connexion mémorisée.',
      '⚠  Limite YouTube : 10 000 unités/jour.',
    ],
    'spotify_input_label':       'URL de la playlist Spotify',
    'spotify_input_placeholder': 'https://open.spotify.com/playlist/...',

    // SoundCloud
    'soundcloud_what': 'Récupère tous les titres d\'une playlist SoundCloud publique et les importe automatiquement dans une nouvelle playlist YouTube.',
    'soundcloud_needs': [
      'L\'URL de ta playlist SoundCloud',
      'La playlist doit être publique',
      'Une connexion internet',
      '✅  Connexion mémorisée.',
    ],
    'soundcloud_input_label':       'URL de la playlist SoundCloud',
    'soundcloud_input_placeholder': 'https://soundcloud.com/user/sets/playlist',

    // Apple Music
    'apple_what': 'Récupère tous les titres d\'une playlist Apple Music publique et les importe automatiquement dans une nouvelle playlist YouTube.',
    'apple_needs': [
      'L\'URL de ta playlist Apple Music',
      'La playlist doit être publique',
      'Une connexion internet',
      '✅  Connexion mémorisée.',
    ],
    'apple_input_label':       'URL de la playlist Apple Music',
    'apple_input_placeholder': 'https://music.apple.com/fr/playlist/...',

    // YouTube
    'youtube_what': 'Télécharge toutes les vidéos d\'une playlist YouTube et les convertit en fichiers MP3 (192 kbps).',
    'youtube_needs': [
      'L\'URL complète de la playlist YouTube',
      'Une connexion internet',
    ],
    'youtube_input_label':       'URL de la playlist YouTube',
    'youtube_input_placeholder': 'https://www.youtube.com/playlist?list=...',

    // Excel
    'excel_what': 'Lit un fichier Excel contenant une liste de titres et télécharge chaque chanson en MP3.',
    'excel_needs': [
      'Un fichier Excel avec les titres musicaux',
      'Une connexion internet',
    ],
    'excel_input_file_label':       'Fichier Excel',
    'excel_input_file_placeholder': 'Appuyer pour choisir...',
    'excel_input_name_label':       'Nom de la playlist',
    'excel_input_name_placeholder': 'ex : 1er mai 2026',

    // Erreurs
    'err_no_deezer_id':        'Erreur : veuillez entrer un ID de playlist Deezer.',
    'err_invalid_deezer_id':   'Erreur : l\'ID Deezer doit être un nombre.',
    'err_no_spotify_url':      'Erreur : veuillez entrer une URL Spotify.',
    'err_invalid_spotify_url': 'Erreur : URL Spotify invalide.',
    'err_no_sc_url':           'Erreur : veuillez entrer une URL SoundCloud.',
    'err_no_apple_url':        'Erreur : veuillez entrer une URL Apple Music.',
    'err_no_yt_url':           'Erreur : veuillez entrer une URL YouTube.',
    'err_no_excel_file':       'Erreur : veuillez sélectionner un fichier Excel.',
    'err_no_playlist_name':    'Erreur : veuillez entrer un nom de playlist.',

    // Progression
    'in_progress':       'En cours...',
    'done':              'Terminé !',
    'stop':              'Arrêter',
    'coming_soon':       'Bientôt disponible',
    'coming_soon_desc':  'Cette fonctionnalité sera disponible\ndans une prochaine mise à jour.',

    // Connexion
    'login_subtitle':  'Connectez votre compte Google pour\nimporter vos playlists sur YouTube.',
    'connect_google':  'Se connecter avec Google',
    'logout':          'Se déconnecter',

    // Bibliothèque
    'card_library_title': '🎧  Bibliothèque',
    'card_library_desc':  'Télécharge des playlists en MP3\net écoute-les hors ligne dans l\'app',
    'library_title':        'Bibliothèque',
    'library_download':     'Télécharger une playlist',
    'library_empty':        'Aucune playlist téléchargée',
    'library_empty_hint':   'Appuie sur le bouton + pour\ntélécharger ta première playlist',
    'library_tracks':       'titres',
    'library_saved':        'sauvegardés',
    'library_play_all':     'Tout lire',
    'library_delete_title': 'Supprimer la playlist ?',
    'library_delete_confirm': 'La playlist "%s" et tous ses titres seront supprimés.',
    'cancel':               'Annuler',
    'delete':               'Supprimer',
  },
  'en': {
    'app_title':        'Playlist Manager',
    'choose_action':    'Choose an action',
    'choose_platform':  'Choose your platform',
    'back':             'Back',
    'launch':           'Run',
    'theme_dark':       'Dark theme',
    'theme_light':      'Light theme',
    'lang_btn':         '🇫🇷 FR',
    'what_it_does':     'What it does',
    'what_you_need':    'What you need',
    'open_folder':      'Open folder',
    'recent_dl':        'Recent downloads',

    'card_streaming_title': 'Streaming  →  YouTube',
    'card_streaming_desc':  'Import a Deezer or Spotify playlist\nto your YouTube library',
    'card_youtube_title':   'YouTube  →  MP3',
    'card_youtube_desc':    'Download a YouTube playlist\nand convert each video to MP3',
    'card_excel_title':     'Excel  →  MP3',
    'card_excel_desc':      'Download tracks in the order\ndefined in an Excel file',

    'card_deezer_title':      'Deezer  →  YouTube',
    'card_deezer_desc':       'Import a Deezer playlist\nto your YouTube library',
    'card_spotify_title':     'Spotify  →  YouTube',
    'card_spotify_desc':      'Import a Spotify playlist\nto your YouTube library',
    'card_soundcloud_title':  'SoundCloud  →  YouTube',
    'card_soundcloud_desc':   'Import a SoundCloud playlist\nto your YouTube library',
    'card_apple_title':       'Apple Music  →  YouTube',
    'card_apple_desc':        'Import an Apple Music playlist\nto your YouTube library',

    'deezer_what': 'Fetches all tracks from a Deezer playlist and automatically imports them into a new YouTube playlist on your Google account.',
    'deezer_needs': [
      'Your Deezer playlist ID  (e.g. 14838804003)',
      'An internet connection',
      'First launch: sign in to your Google account in the browser',
      '✅  Connection remembered — sign in once.',
      '⚠  YouTube limit: 10,000 units/day — each track costs 150 units.',
      '✅  Auto-resume: relaunch with the same ID.',
    ],
    'deezer_input_label':       'Deezer playlist ID',
    'deezer_input_placeholder': 'e.g. 14838804003',

    'spotify_what': 'Fetches all tracks from a Spotify playlist and automatically imports them into a new YouTube playlist on your Google account.',
    'spotify_needs': [
      'Your Spotify playlist URL',
      'The playlist must be public',
      'An internet connection',
      '✅  Connection remembered.',
      '⚠  YouTube limit: 10,000 units/day.',
    ],
    'spotify_input_label':       'Spotify playlist URL',
    'spotify_input_placeholder': 'https://open.spotify.com/playlist/...',

    'soundcloud_what': 'Fetches all tracks from a public SoundCloud playlist and automatically imports them into a new YouTube playlist.',
    'soundcloud_needs': [
      'Your SoundCloud playlist URL',
      'The playlist must be public',
      'An internet connection',
      '✅  Connection remembered.',
    ],
    'soundcloud_input_label':       'SoundCloud playlist URL',
    'soundcloud_input_placeholder': 'https://soundcloud.com/user/sets/playlist',

    'apple_what': 'Fetches all tracks from a public Apple Music playlist and automatically imports them into a new YouTube playlist.',
    'apple_needs': [
      'Your Apple Music playlist URL',
      'The playlist must be public',
      'An internet connection',
      '✅  Connection remembered.',
    ],
    'apple_input_label':       'Apple Music playlist URL',
    'apple_input_placeholder': 'https://music.apple.com/playlist/...',

    'youtube_what': 'Downloads all videos from a YouTube playlist and converts them to MP3 files (192 kbps).',
    'youtube_needs': [
      'The full YouTube playlist URL',
      'An internet connection',
    ],
    'youtube_input_label':       'YouTube playlist URL',
    'youtube_input_placeholder': 'https://www.youtube.com/playlist?list=...',

    'excel_what': 'Reads an Excel file with track titles and downloads each song as MP3.',
    'excel_needs': [
      'An Excel file with track titles',
      'An internet connection',
    ],
    'excel_input_file_label':       'Excel file',
    'excel_input_file_placeholder': 'Tap to choose...',
    'excel_input_name_label':       'Playlist name',
    'excel_input_name_placeholder': 'e.g. Summer 2026',

    'err_no_deezer_id':        'Error: please enter a Deezer playlist ID.',
    'err_invalid_deezer_id':   'Error: Deezer ID must be a number.',
    'err_no_spotify_url':      'Error: please enter a Spotify URL.',
    'err_invalid_spotify_url': 'Error: invalid Spotify URL.',
    'err_no_sc_url':           'Error: please enter a SoundCloud URL.',
    'err_no_apple_url':        'Error: please enter an Apple Music URL.',
    'err_no_yt_url':           'Error: please enter a YouTube URL.',
    'err_no_excel_file':       'Error: please select an Excel file.',
    'err_no_playlist_name':    'Error: please enter a playlist name.',

    'in_progress':       'In progress...',
    'done':              'Done!',
    'stop':              'Stop',
    'coming_soon':       'Coming soon',
    'coming_soon_desc':  'This feature will be available\nin a future update.',

    // Login
    'login_subtitle':  'Connect your Google account to\nimport your playlists to YouTube.',
    'connect_google':  'Connect with Google',
    'logout':          'Log out',

    // Library
    'card_library_title': '🎧  Library',
    'card_library_desc':  'Download playlists as MP3\nand listen offline in the app',
    'library_title':        'Library',
    'library_download':     'Download a playlist',
    'library_empty':        'No playlists downloaded',
    'library_empty_hint':   'Tap the + button to download\nyour first playlist',
    'library_tracks':       'tracks',
    'library_saved':        'saved',
    'library_play_all':     'Play all',
    'library_delete_title': 'Delete playlist?',
    'library_delete_confirm': 'Playlist "%s" and all its tracks will be deleted.',
    'cancel':               'Cancel',
    'delete':               'Delete',
  },
};
