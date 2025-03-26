import os
import time
from threading import Thread

from dotenv import load_dotenv
from PIL import Image

from controller import Controller
from shared import Results, Runner
from waveshare import EPD, GT1151, GtDevelopment


class MainApp:
    flag_t: int
    gt_dev: GtDevelopment
    gt_old: GtDevelopment
    gt: GT1151
    epd: EPD
    t: Thread
    controller: Controller
    runner: Runner

    def __init__(self):
        try:
            load_dotenv()
            self.flag_t = 1
            self.gt_dev = GtDevelopment()
            self.gt_old = GtDevelopment()
            self.gt = GT1151()
            self.epd = EPD()

            print("init and clear")

            self.epd.init(self.epd.FULL_UPDATE)

            self.gt.gt_init()
            self.epd.clear(0xFF)

            self.controller = Controller()
            self.runner = Runner(self.controller.jobs())

            self.t = Thread(target=self.__pthread_irq)
            self.t.daemon = True
            self.t.start()

            display = self.controller.current_display()
            print("Starting here:", display)
            image = Image.open(display)
            self.epd.display_part_base_image(self.epd.get_buffer(image))
            self.epd.init(self.epd.PART_UPDATE)
        except IOError as e:
            print(e)
        except KeyboardInterrupt:
            self.__keyboard_interrupt()

    def __pthread_irq(self):
        print("pthread running")
        while self.flag_t == 1:
            if self.gt.digital_read(self.gt.INT) == 0:
                self.gt_dev.Touch = 1
            else:
                self.gt_dev.Touch = 0
        print("thread:exit")

    def __keyboard_interrupt(self):
        print("ctrl+c")
        self.flag_t = 0
        self.epd.clear(0xFF)
        time.sleep(0.2)
        self.epd.clear(0xFF)
        self.epd.sleep()
        time.sleep(2)
        self.t.join()
        self.epd.dev_exit()
        exit()

    def __system_action(self, restart: bool = False):
        self.flag_t = 0
        self.epd.clear(0xFF)
        self.epd.sleep()
        time.sleep(2)
        self.t.join()
        self.epd.dev_exit()

        if restart:
            os.system("sudo shutdown -r now")
        else:
            os.system("sudo shutdown now")

    def __run_end(self):
        self.runner.run_pending()
        time.sleep(0.1)

    def __refresh(self):
        self.__update_screen()
        self.epd.clear(0xFF)
        self.epd.clear(0xFF)
        time.sleep(2)
        self.__update_screen()

    def __update_screen(self):
        display = self.controller.current_display()
        print("Changing to:", display)
        new_image = Image.open(display)
        self.epd.display_partial_wait(self.epd.get_buffer(new_image))

    def run(self):
        try:
            while True:
                pending_update = self.controller.pending_update()
                if pending_update != "":
                    print("update:", pending_update)
                    new_image = Image.open(pending_update)
                    self.epd.display_partial_wait(self.epd.get_buffer(new_image))
                    self.__run_end()
                    continue

                self.gt.gt_scan(self.gt_dev, self.gt_old)
                if (
                    not (
                        self.gt_old.X[0] == self.gt_dev.X[0]
                        and self.gt_old.Y[0] == self.gt_dev.Y[0]
                        and self.gt_old.S[0] == self.gt_dev.S[0]
                    )
                    and self.gt_dev.TouchpointFlag
                ):
                    self.gt_dev.TouchpointFlag = 0

                    result = self.controller.touch_event(
                        250 - self.gt_dev.Y[0], self.gt_dev.X[0], self.gt_dev.S[0]
                    )

                    match result:
                        case Results.SUCCESS.value:
                            self.__update_screen()
                        case Results.REFRESH.value:
                            print("refreshing....")
                            self.__refresh()
                        case Results.SHUTDOWN.value:
                            print("Shutting down...")
                            self.__update_screen()
                            time.sleep(2)
                            self.__system_action()
                        case Results.RESTART.value:
                            print("Restarting...")
                            self.__update_screen()
                            time.sleep(2)
                            self.__system_action(True)
                        case _:
                            pass

                self.__run_end()
        except IOError as e:
            print(e)
        except KeyboardInterrupt:
            self.__keyboard_interrupt()

        self.__keyboard_interrupt()


if __name__ == "__main__":
    main_app = MainApp()
    main_app.run()
