from .lump_device import LumpDevice

class ColorSensor(LumpDevice):
    def __init__(self, tx, rx, freq=10):
        super().__init__(tx, rx, freq)

    def set_mode_hsv(self):
        self.set_mode(self.get_mode_index_by_name("HSV"))

    def set_mode_shsv(self):
        self.set_mode(self.get_mode_index_by_name("SHSV"))

    def get_hsv(self):
        mode = self.get_mode_index_by_name("HSV")
        h = self.modes[mode].data[0]
        s = self.modes[mode].data[1]
        v = self.modes[mode].data[2]
        return h, s, v

    def get_shsv(self):
        mode = self.get_mode_index_by_name("SHSV")
        h = self.modes[mode].data[0]
        s = self.modes[mode].data[1]
        v = self.modes[mode].data[2]
        return h, s, v
