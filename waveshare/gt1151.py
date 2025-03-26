from . import epdconfig as config


class GtDevelopment:
    def __init__(self):
        self.Touch = 0
        self.TouchpointFlag = 0
        self.TouchCount = 0
        self.Touchkeytrackid = [0, 1, 2, 3, 4]
        self.X = [0, 1, 2, 3, 4]
        self.Y = [0, 1, 2, 3, 4]
        self.S = [0, 1, 2, 3, 4]


class GT1151:
    def __init__(self):
        # e-Paper
        self.ERST = config.EPD_RST_PIN
        self.DC = config.EPD_DC_PIN
        self.CS = config.EPD_CS_PIN
        self.BUSY = config.EPD_BUSY_PIN
        # TP
        self.TRST = config.TRST
        self.INT = config.INT

    @staticmethod
    def digital_read(pin):
        return config.digital_read(pin)

    def get_reset(self):
        config.digital_write(self.TRST, 1)
        config.delay_ms(100)
        config.digital_write(self.TRST, 0)
        config.delay_ms(100)
        config.digital_write(self.TRST, 1)
        config.delay_ms(100)

    @staticmethod
    def gt_write(reg, data):
        config.i2c_writebyte(reg, data)

    @staticmethod
    def gt_read(reg, gt_len):
        return config.i2c_readbyte(reg, gt_len)

    def gt_read_version(self):
        buf = self.gt_read(0x8140, 4)
        print(buf)

    def gt_init(self):
        self.get_reset()
        self.gt_read_version()

    def gt_scan(self, gt_dev, gt_old):
        buf = []
        mask = 0x00

        if gt_dev.Touch == 1:
            gt_dev.Touch = 0
            buf = self.gt_read(0x814E, 1)

            if buf[0] & 0x80 == 0x00:
                self.gt_write(0x814E, mask)
                config.delay_ms(10)

            else:
                gt_dev.TouchpointFlag = buf[0] & 0x80
                gt_dev.TouchCount = buf[0] & 0x0F

                if gt_dev.TouchCount > 5 or gt_dev.TouchCount < 1:
                    self.gt_write(0x814E, mask)
                    return

                buf = self.gt_read(0x814F, gt_dev.TouchCount * 8)
                self.gt_write(0x814E, mask)

                gt_old.X[0] = gt_dev.X[0]
                gt_old.Y[0] = gt_dev.Y[0]
                gt_old.S[0] = gt_dev.S[0]

                for i in range(0, gt_dev.TouchCount, 1):
                    gt_dev.Touchkeytrackid[i] = buf[0 + 8 * i]
                    gt_dev.X[i] = (buf[2 + 8 * i] << 8) + buf[1 + 8 * i]
                    gt_dev.Y[i] = (buf[4 + 8 * i] << 8) + buf[3 + 8 * i]
                    gt_dev.S[i] = (buf[6 + 8 * i] << 8) + buf[5 + 8 * i]

                print(gt_dev.X[0], gt_dev.Y[0], gt_dev.S[0])
