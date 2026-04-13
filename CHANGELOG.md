# Changelog

## [1.1.0] — 2026-04-13

### Nouveautés

**Interface**
- Thème clair / sombre toggleable depuis toutes les pages
- Historique des 5 derniers téléchargements sur la page d'accueil, avec bouton d'ouverture du dossier
- Barre de progression avec compte de titres et estimation du temps restant (ETA)
- Bouton "Ouvrir le dossier" affiché automatiquement en fin de traitement
- Bouton "Réessayer les titres manquants" pour relancer uniquement les titres en échec (mode Excel)
- Notification sonore + fenêtre mise au premier plan à la fin de chaque traitement

**Mode Excel → MP3**
- Détection automatique des feuilles du fichier Excel (liste déroulante dynamique)
- Paramétrage de la colonne et de la première ligne de données directement dans l'interface
- Pré-sélection intelligente de la feuille "Deezer" si elle existe

**Mode Deezer → YouTube**
- Connexion Google intégrée : plus besoin de fournir un fichier JSON
- Reprise automatique en cas d'interruption (quota dépassé, coupure réseau)
- Page d'aide pour trouver l'ID d'une playlist Deezer

### Stabilité
- Retry automatique (3 tentatives) sur toutes les opérations réseau
- Détection de coupure internet avec attente et reprise automatique
- Pause aléatoire entre les téléchargements pour éviter les bans YouTube
- Sauvegarde des titres non trouvés dans `non_trouves.txt`

### Sécurité
- Token OAuth stocké dans le **Windows Credential Manager** (chiffré par Windows) — plus de `token.json` en clair sur le disque
- Migration automatique depuis un `token.json` existant vers le Credential Manager
- Ouverture de dossier via `os.startfile` — supprime un risque d'injection de commande
- Validation de l'ID Deezer (numérique uniquement) avant tout appel API

### Corrections
- Correction d'un crash au moment de la notification de fin (`attributes()` appelé sur un Frame non-toplevel)

---

## [1.0.0] — 2026-01-xx

- Version initiale
- Modes : Deezer → YouTube, YouTube → MP3, Excel → MP3
- Interface tkinter avec navigation par pages
- Page d'aide pour la création des identifiants Google Cloud
