from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Callable, NewType, Optional

from .coordinates import HitBox, TouchCoordinates

Result = NewType("Result", int)


class Results(Enum):
    NORESPONSE = 0
    SUCCESS = 1
    REFRESH = 2
    SHUTDOWN = 3
    RESTART = 4


@dataclass
class DeskControllerAppButton:
    hit_box: HitBox
    action: Callable[[], Result]


DeskControllerAppButtons = NewType(
    "DeskControllerAppButtons", list[DeskControllerAppButton]
)


@dataclass
class AppJob:
    job: Callable[[], None]
    interval_seconds: int


class DeskControllerApp(ABC):
    app_buttons: DeskControllerAppButtons
    pending_update_display: str

    @abstractmethod
    def touch_event(self, coordinates: TouchCoordinates) -> Result:
        pass

    @abstractmethod
    def display(self) -> str:
        pass

    @abstractmethod
    def error(self) -> str:
        pass

    @abstractmethod
    def pending_update(self) -> str:
        pass

    @abstractmethod
    def periodic_job(self) -> Optional[AppJob]:
        pass
