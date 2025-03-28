from enum import Enum
from queue import Queue
from threading import Thread, Timer
from typing import Callable, Optional

from shared import (
    AppJob,
    DeskControllerApp,
    DeskControllerAppButton,
    DeskControllerAppButtons,
    HitBox,
    Result,
    ResultId,
    Results,
    TouchCoordinates,
)

from .client import Client
from .ui import ImagesMapping


class PlayerId(int, Enum):
    playing = 0
    paused = 1
    next = 2
    back = 3


class PlayerApp(DeskControllerApp):
    current_id: PlayerId
    direction_button: Optional[PlayerId]
    spotify_client: Client
    job_queue: Queue
    worker_thread: Thread

    def __init__(self):
        self.current_id = PlayerId.paused

        self.job_queue = Queue()
        self.worker_thread = Thread(target=self.__worker, args=(self.job_queue,))
        self.worker_thread.start()

        self.pending_update_display = None

        self.spotify_client = Client()
        self.current_id = (
            PlayerId.playing
            if self.spotify_client.check_playback_state()
            else PlayerId.paused
        )

        self.app_buttons = DeskControllerAppButtons(
            [
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=16,
                        x_end=63,
                        y_start=30,
                        y_end=77,
                    ),
                    action=self.__action_closure(PlayerId.back),
                ),
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=101,
                        x_end=148,
                        y_start=30,
                        y_end=77,
                    ),
                    action=self.__action_closure(),
                ),
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=186,
                        x_end=233,
                        y_start=30,
                        y_end=77,
                    ),
                    action=self.__action_closure(PlayerId.next),
                ),
            ]
        )

        print("PlayerApp READY")

    def __action_closure(
        self, player_id: Optional[PlayerId] = None
    ) -> Callable[[], Result]:
        def action() -> Result:
            if player_id is None:
                match self.current_id:
                    case PlayerId.playing:
                        print("pausing")
                        self.current_id = PlayerId.paused
                    case PlayerId.paused:
                        print("playing")
                        self.current_id = PlayerId.playing

                self.__client_action(self.current_id)
                return Result(
                    result=ResultId(Results.SUCCESS.value), display_path=self.display()
                )

            if self.current_id is not PlayerId.playing:
                return Result(
                    result=ResultId(Results.NORESPONSE.value), display_path=""
                )

            match player_id:
                case PlayerId.next:
                    print("going to next song")
                case PlayerId.back:
                    print("going to previous song")

            self.current_id = player_id
            self.__client_action(player_id)
            return Result(
                result=ResultId(Results.SUCCESS.value), display_path=self.display()
            )

        return action

    def __client_action(self, player_id: PlayerId) -> None:
        print("doing action", player_id.name)

        match player_id:
            case PlayerId.playing:
                self.spotify_client.start_playback()
            case PlayerId.paused:
                self.spotify_client.pause_playback()
            case PlayerId.next:
                self.spotify_client.next_track()
            case PlayerId.back:
                self.spotify_client.previous_track()
            case _:
                return

    def touch_event(self, coordinates: TouchCoordinates) -> None:
        for app_button in self.app_buttons:
            if coordinates.check_hit(app_button.hit_box):
                self.job_queue.put(app_button.action)

    def __return_to_base(self):
        self.current_id = PlayerId.playing
        self.pending_update_display = Result(
            result=ResultId(Results.SUCCESS.value),
            display_path=ImagesMapping.player_playing,
        )

    def display(self) -> str:
        match self.current_id:
            case PlayerId.playing:
                return ImagesMapping.player_playing
            case PlayerId.paused:
                return ImagesMapping.player_paused
            case PlayerId.next:
                Timer(1, self.__return_to_base).start()
                return ImagesMapping.player_playing_next
            case PlayerId.back:
                Timer(1, self.__return_to_base).start()
                return ImagesMapping.player_playing_back
            case _:
                return ImagesMapping.error

    def error(self) -> str:
        return ImagesMapping.error

    def pending_update(self) -> Optional[Result]:
        to_return = self.pending_update_display
        self.pending_update_display = None

        return to_return

    def periodic_job(self) -> Optional[AppJob]:
        def job():
            print("checking current player state")

            state = self.spotify_client.check_playback_state()

            if state and self.current_id.playing is not PlayerId.playing:
                self.pending_update_display = ImagesMapping.player_playing
                self.current_id = PlayerId.playing
                return

            if not state and self.current_id is PlayerId.playing:
                self.pending_update_display = ImagesMapping.player_paused
                self.current_id = PlayerId.paused
                return

        return AppJob(
            job=job,
            interval_seconds=60,
        )

    def clean_up(self) -> None:
        self.job_queue.put(None)
        self.worker_thread.join()

        print("Spotify cleaned up")

    def __worker(self, job_queue: Queue) -> None:
        while True:
            job: Optional[Callable[[], Result]] = job_queue.get(block=True)
            if job is None:
                print("Spotify worker closing")
                break

            try:
                self.pending_update_display = job()
            except:
                self.pending_update_display = Result(
                    result=ResultId(Results.NORESPONSE.value), display_path=self.error()
                )

            job_queue.task_done()
