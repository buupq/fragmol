class file():
    def __init__(self, filename="fmo.inp", filetype="fmo", keywordsFile="fmoKeywords.inp"):
        self.filename = filename
        self.filetype = filetype
        self.keywordsFile = keywordsFile
        self.isFmo = False
        self.isGaussview = False
        if self.filetype == "fmo":
            self.isFmo = True
            self.numfrags = 0
            self.indat = []
            self.fmoxyz = []
            self.fmobnd = []
            self.fmobnd_extra = []
            self.maxbnd = 0
            self.numAtomInFrags = [0]
            self.numfrag = "nfragwww"
        elif self.filetype == "gaussview":
            self.isGaussview = True
            self.xyz = []

    def write_fixed_keywords(self):
        with open(self.keywordsFile, "r") as kf:
            lines = kf.readlines()
            with open(self.filename, "w") as mf:
                mf.writelines(lines)

    def write_fmo_numfrag(self,numfrag):
        with open(self.filename, "a") as f:
            f.write(" $FMO\n")
            f.write(" NFRAG = {} \n".format(numfrag))
            f.write(" $END\n")

    def write_fmo_indat(self,indat):
        with open(self.filename, "a") as f:
            f.write(" $FMO\n")
            f.write("  indat(1)= \n")
            for line in indat:
                f.write("0 \n")
                f.write(line)
            f.write("0 \n")
            f.write(" $END\n")

    def write_fmoxyz(self,fmoxyz):
        with open(self.filename, "a") as f:
            f.write(" $FMOXYZ\n")
            for line in fmoxyz:
                f.write(line)
            f.write(" $END\n")

    def write_fmobnd(self,fmobnd):
        with open(self.filename, "a") as f:
            f.write(" $FMOBND\n")
            for line in fmobnd:
                f.write(line)
            f.write(" $END\n")

    def write_fmobnd_extra(self,fmobnd_extra):
        with open(self.filename, "a") as f:
            f.write("!!!$FMOBND\n")
            for line in fmobnd_extra:
                f.write(line)
            f.write("!!!$END\n")

    def write_fmo_maxbnd(self, maxbnd):
        with open(self.filename, "a") as f:
            f.write(" $FMO\n")
            f.write("MAXBND={} \n".format(maxbnd))
            f.write(" $END\n")

    def write_final_fmo(self,isExtra=False):
        self.write_fixed_keywords()
        self.write_fmo_numfrag(self.numfrag)
        self.write_fmo_indat(self.indat)
        self.write_fmoxyz(self.fmoxyz)
        self.write_fmobnd(self.fmobnd)
        if isExtra:
            self.write_fmobnd_extra(self.fmobnd_extra)
        self.write_fmo_maxbnd(self.maxbnd)

    def write_xyz(self,xyz):
        with open(self.filename, "a") as f:
            for line in xyz:
                f.write(line)

    def write_final_gaussview_input(self):
        self.write_fixed_keywords()
        self.write_xyz(self.xyz)

