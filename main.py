import sys
import numpy as np
from fragment import fragment
from files import file
from atom import  atom

'''
Step 1:
    - Start with a file containing fragments
    - Split it into individual fragments and write into files
    - Each fragment in each file can be still big
Step 2:
    - If needed, we can further resulting fragments in step 1 using external softwares
    - Start the second round of fragmenting each individual fragment
Step 3:
    - Find bonds connecting fragments
Step 4:
    - Collecting information: 
        - total number of fragment
        - atoms in each fragment (indat)
        - fmoxyz coordinates
    - Write final fmo input file
'''

'''
Step 0
    - instantiate file objects
    - One is default "fmo.inp"
    - One is gaussview style to vidualize when needed
'''
finalFmoInpFile = file()
finalGaussviewInpFile = file(filename="sorted.gjf", filetype="gaussview", keywordsFile="gaussviewKeywords.gjf")


'''
Step 1: Split starting *.gjf file into single fragment files
    - Read grandpa file containing entire target molecular system
    - Split it to fragments
'''
# grandpaFile = fragment(filename="1l.gjf")
# filename="test.gjf"
# filename="1l_6.gjf"
# filename="2l.gjf"
# filename="3l.gjf"
# filename="10l.gjf"
filename="22l.gjf"
grandpaFile = fragment(filename=filename)
grandpaFile.split_fragments()

# print some warning information
print("After Step 1, <<{}>> has been splitted into fragments. These include:".format(filename))
ifrag = 0
for file in grandpaFile.splittedFragFilenames:
    ifrag += 1
    print("     ({}) {}".format(ifrag, file))
print("Take some time to look at these fragments. You can further fragment them.")
isGoing = input("When you finish, type <<GO>> if you want to continue:  \n")
if isGoing == "GO":
    pass
else:
    print("<<<STOP>>>")
    sys.exit()


'''
Step 2: Further splitting fragment files into <<single>> fragment files. 
        Multiple fragment file is because we may use gaussview in the middle to futher fragment it.
    - Loop over all fragments generated from Step 1
    - Further split them into smaller fragment files if they contain more than 1 fragments
'''
singleFragFilenames = []
for parentName in grandpaFile.splittedFragFilenames:
    parentFile = fragment(parentName)
    parentFile.split_fragments()
    singleFragFilenames.extend(parentFile.splittedFragFilenames)

# total number of fragments after the second round of fragmenting
numfrags = len(singleFragFilenames)

# add the number of fragment into fmo file object.
finalFmoInpFile.numfrag = numfrags


'''
Step 2*:
    - Loop over all single fragment files
    - Get the number of fragments
'''

clf = open("corresponding_list.txt","w")

atomNum = 0
ifrag = 0
for child in singleFragFilenames:
    ifrag += 1
    clf.write("({}): <<{}>> \n".format(ifrag, child))

    childFile = fragment(child)
    lines = childFile.get_coord_gaussview(child)
    finalFmoInpFile.numAtomInFrags.append(len(lines))
    indatStart = atomNum + 1

    for line in lines:
        atomNum += 1
        a = atom(line)
        fmoline = "{} {} {} {} {} \n".format(atomNum,a.symbol,a.coord[0], a.coord[1], a.coord[2] )
        finalFmoInpFile.fmoxyz.append(fmoline)
        gaussviewline = "{}(Fragment={}) {} {} {} \n".format(a.symbol,ifrag, a.coord[0], a.coord[1], a.coord[2])
        finalGaussviewInpFile.xyz.append(gaussviewline)
    indatEnd = atomNum
    finalFmoInpFile.indat.append("{} -{} \n".format(indatStart,indatEnd))

clf.close()


finalGaussviewInpFile.write_final_gaussview_input()

# print(finalGaussviewInpFile.xyz)

# lines = childFile.get_coord_gaussview("bigger_Fragment_2.gjf")
# for line in lines:
#     print(line)

first = 0
fragmented_bonds = []
ipair = 0
for firstChild in singleFragFilenames[:numfrags-1]:
    first += 1
    firstChildFile = fragment(firstChild)
    firstLines = firstChildFile.get_coord_gaussview(firstChild)

    second = first
    numConnect = 0
    for secondChild in singleFragFilenames[first:]:
        second += 1
        secondChildFile = fragment(secondChild)
        secondLines = secondChildFile.get_coord_gaussview(secondChild)

        # if numConnect < 4:
        # firstAtomNum = sum([i for i in firstChildFile.numAtomInFrags[:first]])
        isConnect = False
        firstAtomNum = sum([i for i in finalFmoInpFile.numAtomInFrags[:first]])
        for firstLine in firstLines:
            firstAtomNum += 1
            firstAtom = atom(firstLine)
            if firstAtom.skip:
                continue

            # secondAtomNum = sum([i for i in secondChildFile.numAtomInFrags[:second]])
            secondAtomNum = sum([i for i in finalFmoInpFile.numAtomInFrags[:second]])
            for secondLine in secondLines:
                secondAtomNum += 1
                secondAtom = atom(secondLine)
                if secondAtom.skip:
                    continue

                bondThreshold = firstAtom.rad + secondAtom.rad
                distance = np.sum((firstAtom.coord - secondAtom.coord)**2)

                if distance < bondThreshold:
                    isConnect = True
                    if firstAtom.symbol == "Si":
                        fmobnd = "-{} {} \n".format(firstAtomNum,secondAtomNum)
                    else:
                        fmobnd = "-{} {} \n".format(secondAtomNum, firstAtomNum)

                    finalFmoInpFile.fmobnd.append(fmobnd)

                    # write extra info on bond breaking
                    fmobnd_extra = "{}: -{} {}: {} \n".format(first, firstAtomNum, secondAtomNum, second)
                    finalFmoInpFile.fmobnd_extra.append(fmobnd_extra)

                    finalFmoInpFile.maxbnd += 1
                    # numBreakingBonds += 1
                    # print(frag_bond)
        if isConnect:
            ipair += 1
            numConnect += 1
            print("({}): connection pair <<{}>>: <<{}>> - <<{}>>".format(ipair, numConnect, firstChild, secondChild))


# print(fragmented_bonds)
# print(finalFmoInpFile.fmobnd)
finalFmoInpFile.maxbnd += 1

finalFmoInpFile.write_final_fmo(isExtra=True)

# #
# #
# # child = file("test_Fragment_1.gjf")
# # lines = child.get_coord_gaussview()
# # for line in lines:
# #     atom1 = atom(line)
# #     # print(atom1.symbol)


