import select
import sys
import time

import st7789
import vga1_8x16 as font1
import vga1_16x32 as font
from machine import SPI, Pin

from PiBeam import IR_Transmitter

spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
tft = st7789.ST7789(
    spi,
    135,
    240,
    reset=Pin(12, Pin.OUT),
    cs=Pin(9, Pin.OUT),
    dc=Pin(8, Pin.OUT),
    backlight=Pin(13, Pin.OUT),
    rotation=1,
)


def info():
    tft.init()
    tft.text(font, "SB COMPONENTS", 10, 20)
    tft.fill_rect(10, 60, 210, 10, st7789.RED)
    tft.text(font, "PiBeam", 10, 75, st7789.YELLOW)
    time.sleep(1)
    tft.fill(0)
    tft.text(font, "Thanks For", 40, 20)
    tft.text(font, "Buying..!", 40, 75, st7789.YELLOW)
    time.sleep(1)
    tft.fill(0)
    tft.text(font1, "Press Button!", 10, 20)


info()


def read_serial_data():
    poll_obj = select.poll()
    poll_obj.register(sys.stdin, select.POLLIN)

    result = poll_obj.poll(1)
    if result:
        return sys.stdin.readline().strip()
    else:
        return None


tx = IR_Transmitter
tx = tx.NEC()
addr = 0x0000


def transmitter(data):
    tx.transmit(addr, data)
    print("Addr {:04x}".format(addr), "Data {:02x}".format(data))


def display_command(data):
    tft.fill(0)
    tft.text(font, "Data {:02x}".format(data), 50, 20, st7789.YELLOW)
    tft.text(font, "Addr {:04x}".format(addr), 50, 60, st7789.YELLOW)
    time.sleep(3)
    tft.fill(0)


while True:
    received_data = read_serial_data()
    if received_data is None:
        continue

    if received_data == "COMMAND_1":
        data = 0x08
    elif received_data == "COMMAND_2":
        data = 0x0A
    elif received_data == "COMMAND_3":
        data = 0x0C
    else:
        continue

    transmitter(data)
    display_command(data)
