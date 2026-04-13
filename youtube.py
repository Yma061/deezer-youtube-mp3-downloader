import os
import sys
import time
import keyring
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/youtube"]

_KEYRING_SERVICE = "PlaylistManager"
_KEYRING_USER    = "youtube_token"


def _app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _secret_path():
    """Chemin vers client_secret.json (embarqué dans le .exe ou dans le dossier projet)."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "client_secret.json")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "client_secret.json")


def _load_token():
    """Charge le token depuis le Credential Manager Windows (ou migre depuis token.json)."""
    # Migration : si un token.json existe encore, on le migre puis on le supprime
    legacy_path = os.path.join(_app_dir(), "token.json")
    if os.path.exists(legacy_path):
        try:
            with open(legacy_path, "r", encoding="utf-8") as f:
                data = f.read()
            keyring.set_password(_KEYRING_SERVICE, _KEYRING_USER, data)
            os.remove(legacy_path)
        except Exception:
            pass

    data = keyring.get_password(_KEYRING_SERVICE, _KEYRING_USER)
    if not data:
        return None
    try:
        return Credentials.from_authorized_user_info(
            __import__("json").loads(data), SCOPES
        )
    except Exception:
        return None


def _save_token(creds):
    """Sauvegarde le token dans le Credential Manager Windows."""
    keyring.set_password(_KEYRING_SERVICE, _KEYRING_USER, creds.to_json())


def get_youtube_service():
    creds = _load_token()

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Rafraîchissement du token Google...")
            creds.refresh(Request())
        else:
            print("Connexion à Google (une fenêtre va s'ouvrir dans le navigateur)...")
            flow = InstalledAppFlow.from_client_secrets_file(_secret_path(), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
            print("Connexion réussie !")

        _save_token(creds)

    return build("youtube", "v3", credentials=creds)


def create_playlist(youtube, title):
    response = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title},
            "status": {"privacyStatus": "private"}
        }
    ).execute()
    return response["id"]


class QuotaExceededError(Exception):
    pass


def add_videos(youtube, playlist_id, tracks, start_index=0, on_success=None):
    total = len(tracks)
    for i, track in enumerate(tracks):
        if i < start_index:
            continue
        try:
            search = youtube.search().list(
                q=track, part="snippet", type="video", maxResults=1
            ).execute()

            if search["items"]:
                video_id = search["items"][0]["id"]["videoId"]
                youtube.playlistItems().insert(
                    part="snippet",
                    body={"snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id}
                    }}
                ).execute()

                print(f"[{i+1}/{total}] Ajouté : {track}")
                time.sleep(1)
                if on_success:
                    on_success(i + 1)

        except HttpError as e:
            if e.resp.status == 403 and any(
                r in str(e) for r in ("quotaExceeded", "dailyLimitExceeded")
            ):
                raise QuotaExceededError(i)
            print(f"Erreur pour {track} : {e}")
            time.sleep(2)
