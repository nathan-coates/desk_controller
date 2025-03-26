import os
from dataclasses import dataclass

from python_hue_v2 import Hue
from python_hue_v2.grouped_light import GroupedLight


@dataclass
class Light:
    controller: GroupedLight
    state: bool


class Client:
    hue: Hue
    hue_light_ids: list[str]
    hue_lights: dict[str, Light]

    def __init__(self):
        bridge_ip = os.getenv("HUE_IP", "")
        if bridge_ip == "" or bridge_ip == "xxxx":
            raise ValueError("Missing Hue IP")

        bridge_key = os.getenv("HUE_USERNAME", "")
        if bridge_key == "" or bridge_key == "xxxx":
            raise ValueError("Missing Hue Key")

        hue_lights_str = os.getenv("HUE_LIGHTS", "")
        if hue_lights_str == "" or hue_lights_str == "xxxx":
            raise ValueError("Missing Hue Lights")

        self.hue_light_ids = hue_lights_str.split(",")

        self.hue = Hue(ip_address=bridge_ip, hue_application_key=bridge_key)

        self.hue_lights = {}
        for gl in self.hue.grouped_lights:
            if gl.grouped_light_id in self.hue_light_ids:
                self.hue_lights[gl.grouped_light_id] = Light(controller=gl, state=gl.on)

        keys = [x for x in self.hue_lights.keys()]
        for light_id in self.hue_light_ids:
            if light_id not in keys:
                raise ValueError("Provided id was not found", light_id)

        print("Hue READY")

    def get_light_state(self, light_id: str) -> bool:
        light = self.hue_lights[light_id]
        light.state = light.controller.on
        return light.state

    def turn_on_light(self, light_id) -> None:
        light = self.hue_lights[light_id]

        if not light.state:
            print("turning on light", light_id)
            light.controller.set_state(True, 100, None)

    def turn_off_light(self, light_id) -> None:
        light = self.hue_lights[light_id]

        if light.state:
            print("turning off light", light_id)
            light.controller.set_state(False, None, None)
