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


class ComputerId(str, Enum):
    macMini = "Mac Mini"
    workMac = "Work Mac"
    desktop = "Desktop"


class KVMApp(DeskControllerApp):
    current_id: ComputerId
    command_mapping: dict[ComputerId, str]
    client: Client
    job_queue: Queue
    worker_thread: Thread

    def __init__(self):
        self.client = Client()

        self.job_queue = Queue()
        self.worker_thread = Thread(target=self.__worker, args=(self.job_queue,))
        self.worker_thread.start()

        self.current_id = ComputerId.macMini

        self.pending_update_display = None

        self.command_mapping = {
            ComputerId.macMini: "COMMAND_1",
            ComputerId.workMac: "COMMAND_2",
            ComputerId.desktop: "COMMAND_3",
        }

        self.app_buttons = DeskControllerAppButtons(
            [
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=16,
                        x_end=63,
                        y_start=30,
                        y_end=77,
                    ),
                    action=self.__action_closure(ComputerId.macMini),
                ),
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=101,
                        x_end=148,
                        y_start=30,
                        y_end=77,
                    ),
                    action=self.__action_closure(ComputerId.workMac),
                ),
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=186,
                        x_end=233,
                        y_start=30,
                        y_end=77,
                    ),
                    action=self.__action_closure(ComputerId.desktop),
                ),
            ]
        )

        self.__send_command(ComputerId.macMini)
        print("KVMApp READY")

    def __action_closure(self, computer_id: ComputerId) -> Callable[[], Result]:
        def action() -> Result:
            if self.current_id != computer_id:
                print("Switching to computer", computer_id.value)
                self.current_id = computer_id
                self.__send_command(computer_id)

                return Result(
                    result=ResultId(Results.SUCCESS.value), display_path=self.display()
                )

            return Result(result=ResultId(Results.NORESPONSE.value), display_path="")

        return action

    def __send_command(self, computer_id: ComputerId) -> None:
        print("sending command", self.command_mapping[computer_id])

    def touch_event(self, coordinates: TouchCoordinates) -> None:
        for app_button in self.app_buttons:
            if coordinates.check_hit(app_button.hit_box):
                self.job_queue.put(app_button.action)

    def display(self) -> str:
        match self.current_id:
            case ComputerId.macMini:
                return ImagesMapping.mac_mini
            case ComputerId.workMac:
                return ImagesMapping.work_mac
            case ComputerId.desktop:
                return ImagesMapping.desktop
            case _:
                return ""

    def error(self) -> str:
        return ImagesMapping.error

    def pending_update(self) -> Optional[Result]:
        to_return = self.pending_update_display
        self.pending_update_display = None

        return to_return

    def periodic_job(self) -> Optional[AppJob]:
        return None

    def clean_up(self) -> None:
        self.job_queue.put(None)
        self.worker_thread.join()

        print("KVM cleaned up")

    def __worker(self, job_queue: Queue) -> None:
        while True:
            job: Optional[Callable[[], Result]] = job_queue.get(block=True)
            if job is None:
                print("KVM worker closing")
                break

            try:
                self.pending_update_display = job()
            except Exception as e:
                print("Exception from KVM occured", str(e))
                self.pending_update_display = Result(
                    result=ResultId(Results.NORESPONSE.value), display_path=self.error()
                )

            job_queue.task_done()
