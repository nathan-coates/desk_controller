# *****************************************************************************
# * | File        :	  epd2in13_V4.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2023-08-14
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


import logging

from . import epdconfig

# Display resolution
EPD_WIDTH = 122
EPD_HEIGHT = 250

logger = logging.getLogger(__name__)


class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.EPD_RST_PIN
        self.dc_pin = epdconfig.EPD_DC_PIN
        self.busy_pin = epdconfig.EPD_BUSY_PIN
        self.cs_pin = epdconfig.EPD_CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        epdconfig.address = 0x14

    FULL_UPDATE = 0
    PART_UPDATE = 1

    """
    function :Hardware reset
    parameter:
    """

    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20)
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(2)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20)

    """
    function :send command
    parameter:
     command : Command register
    """

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    """
    function :send data
    parameter:
     data : Write data
    """

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data2(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte(data)
        epdconfig.digital_write(self.cs_pin, 1)

    """
    function :Wait until the busy_pin goes LOW
    parameter:
    """

    def read_busy(self):
        logger.debug("e-Paper busy")
        while epdconfig.digital_read(self.busy_pin) == 1:  # 0: idle, 1: busy
            epdconfig.delay_ms(10)
        logger.debug("e-Paper busy release")

    """
    function : Turn On Display
    parameter:
    """

    def turn_on_display(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xF7)
        self.send_command(0x20)  # Activate Display Update Sequence
        self.read_busy()

    """
    function : Turn On Display Part
    parameter:
    """

    def turn_on_display_part(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xFF)  # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20)  # Activate Display Update Sequence
        # self.ReadBusy()

    def turn_on_display_part_wait(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xFF)  # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20)  # Activate Display Update Sequence
        self.read_busy()

    """
    function : Setting the display window
    parameter:
        xstart : X-axis starting position
        ystart : Y-axis starting position
        xend : End position of X-axis
        yend : End position of Y-axis
    """

    def set_window(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44)  # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start >> 3) & 0xFF)
        self.send_data((x_end >> 3) & 0xFF)

        self.send_command(0x45)  # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    """
    function : Set Cursor
    parameter:
        x : X-axis starting position
        y : Y-axis starting position
    """

    def set_cursor(self, x, y):
        self.send_command(0x4E)  # SET_RAM_X_ADDRESS_COUNTER
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data(x & 0xFF)

        self.send_command(0x4F)  # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)

    """
    function : Initialize the e-Paper register
    parameter:
    """

    def init(self, update):
        if epdconfig.module_init() != 0:
            return -1

        if update == self.FULL_UPDATE:
            # EPD hardware init start
            self.reset()

            self.read_busy()
            self.send_command(0x12)  # SWRESET
            self.read_busy()

            self.send_command(0x01)  # Driver output control
            self.send_data(0xF9)
            self.send_data(0x00)
            self.send_data(0x00)

            self.send_command(0x11)  # data entry mode
            self.send_data(0x03)

            self.set_window(0, 0, self.width - 1, self.height - 1)
            self.set_cursor(0, 0)

            self.send_command(0x3C)
            self.send_data(0x05)

            self.send_command(0x21)  #  Display update control
            self.send_data(0x00)
            self.send_data(0x80)

            self.send_command(0x18)
            self.send_data(0x80)

            self.read_busy()

        else:
            epdconfig.digital_write(self.reset_pin, 0)
            epdconfig.delay_ms(1)
            epdconfig.digital_write(self.reset_pin, 1)

            self.send_command(0x01)  # Driver output control
            self.send_data(0xF9)
            self.send_data(0x00)
            self.send_data(0x00)

            self.send_command(0x3C)  # BorderWavefrom
            self.send_data(0x80)

            self.send_command(0x11)  # data entry mode
            self.send_data(0x03)

            self.set_window(0, 0, self.width - 1, self.height - 1)
            self.set_cursor(0, 0)

        return 0

    """
    function : Display images
    parameter:
        image : Image data
    """

    def get_buffer(self, image):
        img = image
        imwidth, imheight = img.size
        if imwidth == self.width and imheight == self.height:
            img = img.rotate(180, expand=True).convert("1")
        elif imwidth == self.height and imheight == self.width:
            # image has correct dimensions, but needs to be rotated
            img = img.rotate(270, expand=True).convert("1")
        else:
            logger.warning(
                "Wrong image dimensions: must be "
                + str(self.width)
                + "x"
                + str(self.height)
            )
            # return a blank buffer
            return [0x00] * (int(self.width / 8) * self.height)

        buf = bytearray(img.tobytes("raw"))
        return buf

    """
    function : Sends the image buffer in RAM to e-Paper and displays
    parameter:
        image : Image data
    """

    def display(self, image):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1

        self.send_command(0x24)
        # for j in range(0, self.height):
        # for i in range(0, linewidth):
        # self.send_data(image[i + j * linewidth])

        self.send_data2(image)
        self.turn_on_display()

    """
    function : Sends the image buffer in RAM to e-Paper and partial refresh
    parameter:
        image : Image data
    """

    def display_partial(self, image):
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(1)
        epdconfig.digital_write(self.reset_pin, 1)

        self.send_command(0x01)  # Driver output control
        self.send_data(0xF9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x11)  # data entry mode
        self.send_data(0x03)

        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(0x24)  # WRITE_RAM
        self.send_data2(image)
        self.turn_on_display_part()

    def display_partial_wait(self, image):
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(1)
        epdconfig.digital_write(self.reset_pin, 1)

        self.send_command(0x01)  # Driver output control
        self.send_data(0xF9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x11)  # data entry mode
        self.send_data(0x03)

        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(0x24)  # WRITE_RAM
        self.send_data2(image)
        self.turn_on_display_part_wait()

    """
    function : Refresh a base image
    parameter:
        image : Image data
    """

    def display_part_base_image(self, image):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1

        self.send_command(0x24)
        for j in range(0, self.height):
            for i in range(0, linewidth):
                self.send_data(image[i + j * linewidth])

        self.send_command(0x26)
        for j in range(0, self.height):
            for i in range(0, linewidth):
                self.send_data(image[i + j * linewidth])
        self.turn_on_display()

    """
    function : Clear screen
    parameter:
    """

    def clear(self, color):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1
        # logger.debug(linewidth)

        self.send_command(0x24)
        for j in range(0, self.height):
            for i in range(0, linewidth):
                self.send_data(color)

        self.turn_on_display()

    """
    function : Enter sleep mode
    parameter:
    """

    def sleep(self):
        self.send_command(0x10)  # enter deep sleep
        self.send_data(0x01)

        epdconfig.delay_ms(2000)

    @staticmethod
    def dev_exit():
        epdconfig.module_exit()


### END OF FILE ###
