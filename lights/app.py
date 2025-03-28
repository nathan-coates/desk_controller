from enum import Enum
from queue import Queue
from threading import Thread
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


class LightId(str, Enum):
    d = "Den"
    lv = "Living Room"
    b = "Bedroom"


class LightsApp(DeskControllerApp):
    id_state: dict[LightId, bool]
    client: Client
    light_id_mapping: dict[LightId, str]
    job_queue: Queue
    worker_thread: Thread

    def __init__(self):
        self.client = Client()

        self.job_queue = Queue()
        self.worker_thread = Thread(target=self.__worker, args=(self.job_queue,))
        self.worker_thread.start()

        ids = self.client.hue_light_ids
        self.light_id_mapping = {
            LightId.d: ids[0],
            LightId.lv: ids[1],
            LightId.b: ids[2],
        }

        self.id_state = {
            LightId.d: self.client.hue_lights[self.light_id_mapping[LightId.d]].state,
            LightId.lv: self.client.hue_lights[self.light_id_mapping[LightId.lv]].state,
            LightId.b: self.client.hue_lights[self.light_id_mapping[LightId.b]].state,
        }

        self.pending_update_display = None

        self.app_buttons = DeskControllerAppButtons(
            [
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=16,
                        x_end=63,
                        y_start=30,
                        y_end=77,
                    ),
                    action=self.__action_closure(LightId.d),
                ),
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=101,
                        x_end=148,
                        y_start=30,
                        y_end=77,
                    ),
                    action=self.__action_closure(LightId.lv),
                ),
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=186,
                        x_end=233,
                        y_start=30,
                        y_end=77,
                    ),
                    action=self.__action_closure(LightId.b),
                ),
            ]
        )

        print("LightsApp READY")

    def __action_closure(self, light_id: LightId) -> Callable[[], Result]:
        def action() -> Result:
            self.__flip_state(light_id)

            return Result(
                result=ResultId(Results.SUCCESS.value), display_path=self.display()
            )

        return action

    def __flip_state(self, light_id: LightId) -> None:
        if self.id_state[light_id]:
            self.client.turn_off_light(self.light_id_mapping[light_id])
        else:
            self.client.turn_on_light(self.light_id_mapping[light_id])

        self.id_state[light_id] = not self.id_state[light_id]

        print(f"{light_id} is now", self.id_state[light_id])

    def touch_event(self, coordinates: TouchCoordinates) -> None:
        for app_button in self.app_buttons:
            if coordinates.check_hit(app_button.hit_box):
                self.job_queue.put(app_button.action)

    def __get_display(self) -> str:
        final = ""
        for key, value in self.id_state.items():
            final += f"{key.name}{str(value).lower()}_"

        print(final)

        match final:
            case "dfalse_lvfalse_bfalse_":
                return ImagesMapping.lights_df_lvf_bdf.value
            case "dfalse_lvfalse_btrue_":
                return ImagesMapping.lights_df_lvf_bdo.value
            case "dfalse_lvtrue_bfalse_":
                return ImagesMapping.lights_df_lvo_bdf.value
            case "dfalse_lvtrue_btrue_":
                return ImagesMapping.lights_df_lvo_bdo.value
            case "dtrue_lvfalse_bfalse_":
                return ImagesMapping.lights_do_lvf_bdf.value
            case "dtrue_lvfalse_btrue_":
                return ImagesMapping.lights_do_lvf_bdo.value
            case "dtrue_lvtrue_bfalse_":
                return ImagesMapping.lights_do_lvo_bdf.value
            case "dtrue_lvtrue_btrue_":
                return ImagesMapping.lights_do_lvo_bdo.value
            case _:
                return ImagesMapping.lights_error.value

    def display(self) -> str:
        return self.__get_display()

    def error(self) -> str:
        return ImagesMapping.lights_error.value

    def pending_update(self) -> Optional[Result]:
        to_return = self.pending_update_display
        self.pending_update_display = None

        return to_return

    def periodic_job(self) -> Optional[AppJob]:
        def job():
            print("checking current lights state")
            needs_update = False

            for key, light_id in self.light_id_mapping.items():
                state = self.client.get_light_state(light_id)
                current_state = self.id_state[key]

                if state != current_state:
                    needs_update = True
                    self.id_state[key] = state

            if needs_update:
                self.pending_update_display = self.display()

        return AppJob(
            job=job,
            interval_seconds=60,
        )

    def clean_up(self) -> None:
        self.job_queue.put(None)
        self.worker_thread.join()

        print("Hue cleaned up")

    def __worker(self, job_queue: Queue) -> None:
        while True:
            job: Optional[Callable[[], Result]] = job_queue.get(block=True)
            if job is None:
                print("Hue worker closing")
                break

            try:
                self.pending_update_display = job()
            except:
                self.pending_update_display = Result(
                    result=ResultId(Results.NORESPONSE.value), display_path=self.error()
                )

            job_queue.task_done()
