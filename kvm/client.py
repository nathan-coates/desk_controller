import os
import time
from typing import TypedDict

import serial


class SerialSettings(TypedDict):
    baudrate: int
    parity: str
    bytesize: int
    stopbits: float


class Client:
    usb_address: str
    serial_mode: SerialSettings

    def __init__(self):
        self.usb_address = os.getenv("KVM_USB_ADDR")
        if self.usb_address == "" or self.usb_address == "xxxx":
            raise ValueError("Missing KVM USB Address")

        self.serial_mode = {
            "baudrate": 115200,
            "parity": serial.PARITY_NONE,
            "bytesize": serial.EIGHTBITS,
            "stopbits": serial.STOPBITS_ONE,
        }

    def send_command(self, command: str) -> None:
        try:
            port = serial.Serial(self.usb_address, **self.serial_mode)
            port.write((command + "\n").encode())
            time.sleep(0.5)
            port.close()
        except serial.SerialException as e:
            print(str(e))
