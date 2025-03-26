import os
from typing import Any, cast

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth


class Client:
    sp: Spotify
    device_id: str

    def __init__(self):
        client_id = os.getenv("SPOTIFY_CLIENT", "")
        if client_id == "" or client_id == "xxxx":
            raise ValueError("Missing Spotify client id")

        client_secret = os.getenv("SPOTIFY_SECRET", "")
        if client_secret == "" or client_secret == "xxxx":
            raise ValueError("Missing Spotify client secret")

        self.device_id = os.getenv("SPOTIFY_DEVICE_ID", "")
        if self.device_id == "" or self.device_id == "xxxx":
            raise ValueError("Missing Spotify device id")

        self.sp = Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri="http://localhost:3000/callback",
                scope=[
                    "user-read-playback-state",
                    "user-modify-playback-state",
                    "user-read-currently-playing",
                ],
            )
        )

        print("Spotify READY")

    def check_playback_state(self) -> bool:
        result = self.sp.current_playback()
        if result is None:
            return False

        return cast(dict[str, Any], result).get("is_playing", False)

    def pause_playback(self) -> None:
        self.sp.pause_playback(device_id=self.device_id)

    def start_playback(self) -> None:
        self.sp.start_playback(device_id=self.device_id)

    def next_track(self) -> None:
        self.sp.next_track(device_id=self.device_id)

    def previous_track(self) -> None:
        self.sp.previous_track(device_id=self.device_id)
