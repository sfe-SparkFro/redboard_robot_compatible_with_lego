class LumpMode:
    FORMAT_DATA_SETS = 0
    FORMAT_FORMAT = 1
    FORMAT_FIGURES = 2
    FORMAT_DECIMALS = 3

    FORMAT_INT8 = 0
    FORMAT_INT16 = 1
    FORMAT_INT32 = 2
    FORMAT_FLOAT = 3

    def __init__(self):
        self.index = 0
        self.name = ""
        self.raw_min = 0
        self.raw_max = 0
        self.pct_min = 0
        self.pct_max = 0
        self.si_min = 0
        self.si_max = 0
        self.units = ""
        self.format = (0, 0, 0, 0)
        self.data = []
