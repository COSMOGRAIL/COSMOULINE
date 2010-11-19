#
#	Scipt to prepare the decompression of liverpool data
#	

import os
import glob
import csv		# for the ouptut
import operator		# for the sorted()
import datetime
import time


################   CONFIGURATION   #######################

#	location of the "yyyy/yyyymmdd/yyyymmdd.*" files : has to end with "/" !
datadir = "/home/epfl/tewes/COSMOGRAIL/DATA_Liverpool/"

decompdir = "/home/epfl/tewes/unsaved/liverdecomp/"

outputlist = "fitslist_liverpool.txt"

full_lens_names_file = "../logscripts/full_lens_names.txt"

lens_to_get = ""

##########################################################


print "HELLO LIVERPOOOOOOOOL !"

globfiles = glob.glob(datadir + "????/????????/*.*")
print "I've found", len(globfiles), "files."

found_extensions = set()
for eachfile in globfiles:
	found_extensions.add(eachfile.split('.')[-1])
print "Extensions of the files :"
print found_extensions

for extension in found_extensions:
	os.system("mkdir " + decompdir + extension)

for eachfile in globfiles:
	extension = eachfile.split('.')[-1]
	cmd = "cp " + eachfile + " " + decompdir + extension + "/."
	os.system(cmd)
	print eachfile

print "Bye !"
exit()
