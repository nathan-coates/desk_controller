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

from .ui import ImagesMapping


class MenuId(int, Enum):
    base = 0
    refresh = 1
    shutdown = 2
    restart = 3


class MenuApp(DeskControllerApp):
    current_id: MenuId
    job_queue: Queue
    worker_thread: Thread

    def __init__(self):
        self.current_id = MenuId.base

        self.pending_update_display = None

        self.job_queue = Queue()
        self.worker_thread = Thread(target=self.__worker, args=(self.job_queue,))
        self.worker_thread.start()

        self.app_buttons = DeskControllerAppButtons(
            [
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=33,
                        x_end=88,
                        y_start=50,
                        y_end=71,
                    ),
                    action=self.__action_closure(MenuId.refresh),
                ),
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=97,
                        x_end=152,
                        y_start=50,
                        y_end=71,
                    ),
                    action=self.__action_closure(MenuId.shutdown),
                ),
                DeskControllerAppButton(
                    hit_box=HitBox(
                        x_start=161,
                        x_end=216,
                        y_start=50,
                        y_end=71,
                    ),
                    action=self.__action_closure(MenuId.restart),
                ),
            ]
        )

        print("MenuApp READY")

    def __action_closure(self, menu_id: MenuId) -> Callable[[], Result]:
        def action() -> Result:
            self.current_id = menu_id

            match menu_id:
                case MenuId.refresh:
                    return Result(
                        result=ResultId(Results.REFRESH.value),
                        display_path=self.display(),
                    )
                case MenuId.shutdown:
                    return Result(
                        result=ResultId(Results.SHUTDOWN.value),
                        display_path=self.display(),
                    )
                case MenuId.restart:
                    return Result(
                        result=ResultId(Results.RESTART.value),
                        display_path=self.display(),
                    )
                case _:
                    return Result(
                        result=ResultId(Results.NORESPONSE.value),
                        display_path=self.display(),
                    )

        return action

    def touch_event(self, coordinates: TouchCoordinates) -> None:
        for app_button in self.app_buttons:
            if coordinates.check_hit(app_button.hit_box):
                self.job_queue.put(app_button.action)

    def __return_to_base(self):
        self.current_id = MenuId.base
        self.pending_update_display = Result(
            result=ResultId(Results.SUCCESS.value), display_path=ImagesMapping.menu_base
        )

    def display(self) -> str:
        match self.current_id:
            case MenuId.base:
                return ImagesMapping.menu_base
            case MenuId.refresh:
                Timer(4, self.__return_to_base).start()
                return ImagesMapping.menu_refresh
            case MenuId.shutdown:
                return ImagesMapping.menu_shutdown
            case MenuId.restart:
                return ImagesMapping.menu_restart
            case _:
                return ImagesMapping.menu_base

    def error(self) -> str:
        return ImagesMapping.menu_base

    def pending_update(self) -> Optional[Result]:
        to_return = self.pending_update_display
        self.pending_update_display = None

        return to_return

    def periodic_job(self) -> Optional[AppJob]:
        return None

    def clean_up(self) -> None:
        self.job_queue.put(None)
        self.worker_thread.join()

        print("Menu cleaned up")

    def __worker(self, job_queue: Queue) -> None:
        while True:
            job: Optional[Callable[[], Result]] = job_queue.get(block=True)
            if job is None:
                print("Menu worker closing")
                break

            try:
                self.pending_update_display = job()
            except:
                self.pending_update_display = Result(
                    result=ResultId(Results.NORESPONSE.value), display_path=self.error()
                )

            job_queue.task_done()
