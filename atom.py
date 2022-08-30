import numpy as np
import json



class atom():
    def __init__(self, line):
        self.line = line

        x = self.line.split()

        self.symbol = x[0][0:2]
        if "(" in self.symbol:
            self.symbol = self.symbol[0]

        self.coord = np.array([float(x[1]), float(x[2]), float(x[3])])

        self.skip = False
        if self.symbol == "H":
            self.nuc = 1
            self.skip = True
        elif self.symbol == "Si":
            self.nuc = 14
            self.rad = 2.1
            # self.rad = 1.11
        elif self.symbol == "O":
            self.nuc = 8
            self.rad = 1.52
            # self.rad = 0.66

        # with open("atominfo.json", "r") as f:
        #     data = json.load(f)
        #


