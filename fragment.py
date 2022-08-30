from os.path import exists
import re

class fragment():
    def __init__(self, filename, filetype="gaussview"):
        # input file name
        self.filename = filename
        # list of fragment names in self.filename
        self.fragnames = []
        # number of fragments in self.filename
        self.numfrags = 0
        # list of the number of atoms of fragments in self.fragnames
        self.numAtomInFrags = []
        self.numAtomInFrags.append(0)
        # list of file names containing single fragments after splitted from self.fragnames
        self.splittedFragFilenames = []
        # fragment-based-sorted content of the self.filename
        self.sortedLines = []
        # if file type is gaussview, use the following pattern to extract fragments
        # more file types will be supported in the future
        self.filetype = filetype
        if self.filetype == "gaussview":
            self.isGaussview = True
            self.fragment_pattern = "Fragment="
            self.gaussviewKeywordsFile = "gaussviewKeywords.gjf"
            self.gaussviewKeywords = []

    #*#
    def get_coord_gaussview(self, filename):
        # check if filename exists
        isFilename = exists(filename)
        if not isFilename:
            print("{} does not exist!".format(filename))
            return None

        # read parent file "filename" and assign content into "lines" list
        lines = []
        with open(filename, "r") as pf:
            tmp = pf.readlines()
            for line in tmp:
                if self.fragment_pattern in line:
                    lines.append(line)

        # return content
        return lines

    #*#
    def get_all_fragname_gaussview(self, lines, fragment_pattern):
        # get list of fragments
        fragnames = []
        for line in lines:
            if fragment_pattern in line:
                fragnames.append("Fragment=" + re.search('Fragment=(.*)\)', line).group(1))
        return fragnames

    #*#
    def get_keywords_gaussview(self):
        # prepare gjf keywords to write file in gaussview format
        with open(self.gaussviewKeywordsFile, "r") as f:
            self.gaussviewKeywords = f.readlines()

    #*#
    def get_unique_frag_name(self, allFragnames):
        # get list of unique fragment names
        fragnames = []
        for x in allFragnames:
            if x not in fragnames:
                fragnames.append(x)

        # number of fragments
        numfrags = len(fragnames)

        return numfrags, fragnames

    #
    def sort_coord(self, unsortedLines, fragnames):
        # this function also get self.numAtomInAFrag
        sortedLines = []
        numAtomInFrags = []
        for frag in fragnames:
            for line in unsortedLines:
                if frag in line:
                    sortedLines.append(line)
            numAtomInFrags.append(len(sortedLines))

        return numAtomInFrags, sortedLines


    def split_fragments(self, gjfFormat=True, isPrint=False):

        # get content and all fragment names from self.filename
        if self.isGaussview:
            unsortedLines = self.get_coord_gaussview(filename=self.filename)
            allFragnames = self.get_all_fragname_gaussview(lines=unsortedLines,fragment_pattern=self.fragment_pattern)

        # get number of frags and unique fragment names
        self.numfrags, self.fragnames = self.get_unique_frag_name(allFragnames=allFragnames)


        # if there is only 1 fragment in self.filename => no need to split
        if self.numfrags == 1:
            if isPrint:
                print("There is only one fragment in {} => no file splitting".format(self.filename))
                self.sortedLines = unsortedLines
            return self.splittedFragFilenames.append(self.filename)

        # print fragment information
        if isPrint:
            print("In the file: {}, there are {} fragments.".format(self.filename, self.numfrags))
            print("These includes:")
            for x in self.fragnames:
                print(x)

        # get sorted self.sortedLines and corresponding self.numAtomInFrags
        numAtomInFrags, self.sortedLines = self.sort_coord(unsortedLines=unsortedLines, fragnames=self.fragnames)
        self.numAtomInFrags.extend(numAtomInFrags)

        # get self.gaussviewKeywords
        if self.isGaussview:
            self.get_keywords_gaussview()

        # loop over fragments in self.filename
        ifrag = 0
        for frag in self.fragnames:
            # file name to write individual fragment from self.filename
            if self.isGaussview:
                fragFilename = self.filename.replace(".gjf", "") + "_" + frag.replace("=","_") + ".gjf"

            self.splittedFragFilenames.append(fragFilename)

            '''
            check if these files exist if they exist with multiple fragment
            inside then we need to ask user if they want to overide the file
            '''

            if exists(fragFilename):
                # get fragment content
                lines = self.get_coord_gaussview(filename=fragFilename)
                # get fragment name in every line
                allFragnames = self.get_all_fragname_gaussview(lines=lines,fragment_pattern=self.fragment_pattern)
                # get number of fragments and their name in fragFile
                numfrags, fragnames = self.get_unique_frag_name(allFragnames=allFragnames)
                # if there is more than 1 frags in fragFile, check if user wants to override fragFile
                if numfrags > 1:
                    print("The file <<{}>> exists with <<{}>> fragments.".format(fragFilename, numfrags))
                    isOveride = input("Do you want to overide it? Yy/Nn? ")
                    if isOveride.strip().upper() == "Y":
                        print("*** override {} ***".format(fragFilename))
                    else:
                        print("*** leave {} as is ***".format(fragFilename))
                        continue

            # print info extracting fragment from self.filename
            if isPrint:
                print("extracting: {} and writing into: {}".format(frag, fragFilename))

            istart = self.numAtomInFrags[ifrag]
            iend = self.numAtomInFrags[ifrag+1]

            # write fragment into fragFile.
            frag = frag + ")"
            with open(fragFilename, "w") as f:
                if self.isGaussview:
                    f.writelines(self.gaussviewKeywords)

                for line in self.sortedLines:
                    if frag in line:
                        f.write(line)
                # f.writelines(self.sortedLines[istart:iend])

            ifrag += 1


