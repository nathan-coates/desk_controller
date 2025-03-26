from enum import Enum
from threading import Timer
from typing import Callable, Optional

from shared import (
    AppJob,
    DeskControllerApp,
    DeskControllerAppButton,
    DeskControllerAppButtons,
    HitBox,
    Result,
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

    def __init__(self):
        self.current_id = MenuId.base

        self.pending_update_display = ""

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
                    print("refreshing...")
                    return Result(Results.REFRESH.value)
                case MenuId.shutdown:
                    print("shutting down...")
                    return Result(Results.SHUTDOWN.value)
                case MenuId.restart:
                    print("restarting...")
                    return Result(Results.RESTART.value)
                case _:
                    print("unknown menu id")
                    return Result(Results.NORESPONSE.value)

        return action

    def touch_event(self, coordinates: TouchCoordinates) -> Result:
        for app_button in self.app_buttons:
            if coordinates.check_hit(app_button.hit_box):
                return app_button.action()

        return Result(Results.NORESPONSE.value)

    def __return_to_base(self):
        self.current_id = MenuId.base
        self.pending_update_display = ImagesMapping.menu_base

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

    def pending_update(self) -> str:
        to_return = self.pending_update_display
        self.pending_update_display = ""

        return to_return

    def periodic_job(self) -> Optional[AppJob]:
        return None
