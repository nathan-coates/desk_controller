from dataclasses import dataclass


@dataclass
class HitBox:
    x_start: int
    x_end: int
    y_start: int
    y_end: int


@dataclass
class TouchCoordinates:
    x: int
    y: int
    s: int

    def check_hit(self, hbox: HitBox) -> bool:
        if self.x < hbox.x_start or self.x > hbox.x_end:
            return False
        if self.y < hbox.y_start or self.y > hbox.y_end:
            return False

        return True
