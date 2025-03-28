from dataclasses import dataclass
from typing import Optional

from kvm import KVMApp
from lights import LightsApp
from menu import MenuApp
from player import PlayerApp
from shared import AppJob, DeskControllerApp, HitBox, Result, ResultId, TouchCoordinates


@dataclass
class App:
    app: DeskControllerApp
    left: Optional["App"]
    right: Optional["App"]
    menu: bool


class Controller:
    current_app: App
    back_app: Optional[App]
    top_hb: HitBox
    menu_hb: HitBox
    left_hb: HitBox
    right_hb: HitBox
    apps: list[App]

    def __init__(self):
        light_app = LightsApp()
        kvm_app = KVMApp()
        player_app = PlayerApp()
        menu_app = MenuApp()

        self.apps = [
            App(
                app=menu_app,
                menu=False,
                left=None,
                right=None,
            ),
            App(
                app=kvm_app,
                menu=True,
                left=None,
                right=None,
            ),
            App(
                app=player_app,
                menu=True,
                left=None,
                right=None,
            ),
            App(
                app=light_app,
                menu=True,
                left=None,
                right=None,
            ),
        ]

        self.current_app = self.apps[1]
        self.back_app = None

        self.top_hb = HitBox(
            x_start=0,
            x_end=250,
            y_start=0,
            y_end=13,
        )

        self.menu_hb = HitBox(
            x_start=97,
            x_end=152,
            y_start=2,
            y_end=13,
        )

        self.left_hb = HitBox(
            x_start=15,
            x_end=70,
            y_start=2,
            y_end=13,
        )

        self.right_hb = HitBox(
            x_start=179,
            x_end=234,
            y_start=2,
            y_end=13,
        )

        self.apps[1].right = self.apps[2]  # linking kvm to player
        self.apps[2].left = self.apps[1]  # linking player to kvm
        self.apps[2].right = self.apps[3]  # linking player to lights
        self.apps[3].left = self.apps[2]  # linking lights to player

        print("Controller READY")

    def current_display(self) -> str:
        return self.current_app.app.display()

    def pending_update(self) -> Optional[Result]:
        return self.current_app.app.pending_update()

    def touch_event(self, x: int, y: int, s: int) -> Optional[Result]:
        coordinates = TouchCoordinates(x, y, s)

        if coordinates.check_hit(self.top_hb):
            print("top bar hit")

            if self.current_app.menu:
                if coordinates.check_hit(self.menu_hb):
                    print("menu hit")
                    self.back_app = self.current_app
                    self.current_app = self.apps[0]

                    return Result(
                        result=ResultId(0), display_path=self.current_app.app.display()
                    )
            else:
                if coordinates.check_hit(self.left_hb):
                    print("back hit")
                    if self.back_app is not None:
                        self.current_app = self.back_app

                    return Result(
                        result=ResultId(0), display_path=self.current_app.app.display()
                    )

            if self.current_app.left is not None:
                if coordinates.check_hit(self.left_hb):
                    print("left option hit")
                    self.current_app = self.current_app.left

                    return Result(
                        result=ResultId(0), display_path=self.current_app.app.display()
                    )

            if self.current_app.right is not None:
                if coordinates.check_hit(self.right_hb):
                    print("right option hit")
                    self.current_app = self.current_app.right

                    return Result(
                        result=ResultId(0), display_path=self.current_app.app.display()
                    )

        self.current_app.app.touch_event(coordinates)
        return None

    def jobs(self) -> list[AppJob]:
        jobs: list[AppJob] = []
        for app in self.apps:
            job = app.app.periodic_job()
            if job is not None:
                jobs.append(job)

        return jobs
