import requests


def get_tracks(playlist_id):
    tracks = []

    playlist_url = f"https://api.deezer.com/playlist/{playlist_id}"
    playlist_response = requests.get(playlist_url).json()

    tracklist_url = playlist_response["tracklist"]

    while tracklist_url:
        response = requests.get(tracklist_url)
        data = response.json()

        for track in data["data"]:
            titre = track["title"]
            artiste = track["artist"]["name"]
            tracks.append(f"{titre} {artiste}")

        tracklist_url = data.get("next")

    return tracks
