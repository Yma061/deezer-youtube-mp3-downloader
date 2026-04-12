from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build




def get_youtube_service(client_secret_path="client_secret.json"):
    scopes = ["https://www.googleapis.com/auth/youtube"]

    flow = InstalledAppFlow.from_client_secrets_file(
        client_secret_path,
        scopes=scopes
    )

    credentials = flow.run_local_server(
        port=0,
        open_browser=True
    )

    return build("youtube", "v3", credentials=credentials)



def create_playlist(youtube, title):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title},
            "status": {"privacyStatus": "private"}
        }
    )
    response = request.execute()
    return response["id"]


import time
from googleapiclient.errors import HttpError



class QuotaExceededError(Exception):
    pass


def add_videos(youtube, playlist_id, tracks, start_index=0, on_success=None):
    total = len(tracks)
    for i, track in enumerate(tracks):
        if i < start_index:
            continue
        try:
            search = youtube.search().list(
                q=track,
                part="snippet",
                type="video",
                maxResults=1
            ).execute()

            if search["items"]:
                video_id = search["items"][0]["id"]["videoId"]

                youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                ).execute()

                print(f"[{i+1}/{total}] Ajouté : {track}")
                time.sleep(1)

                if on_success:
                    on_success(i + 1)

        except HttpError as e:
            if e.resp.status == 403 and any(
                reason in str(e) for reason in ("quotaExceeded", "dailyLimitExceeded")
            ):
                raise QuotaExceededError(i)
            print(f"Erreur pour {track} : {e}")
            time.sleep(2)
