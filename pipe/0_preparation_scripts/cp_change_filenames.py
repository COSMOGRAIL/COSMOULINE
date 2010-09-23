#
#	copy or link "some files" "somewhere else" tweaking the filenames on the way
#

import os, sys, shutil
from glob import glob

################### CONFIGURATION ###################################################################

# ABSOLUTE PATH to where the files are and how to select them :
origpaths = glob("/Users/mtewes/Desktop/change_eso_filename/test/*.png") 

# ABSOLUTE PATH to the directory where you want the aliases/copies :
destdir="/Users/mtewes/Desktop/change_eso_filename/test_dest" 

def newpath(origpath, destdir): 	# specifies how to change the name :
					# origpath is the full path to a present file, and you have to
					# return a full path to the destination file you want.
	
	(dirname, filename) = os.path.split(origpath) # "conscious" splitting of a path
	newfilename = filename.replace(":", "-")
	destpath = os.path.join(destdir, newfilename)
	return destpath

#####################################################################################################


if os.path.isdir(destdir):

	#print "Please remove %s" % destdir	# uncomment these 2 lines if you prefer
	#sys.exit() 

	shutil.rmtree(destdir)
	
os.mkdir(destdir)

for origpath in origpaths:
	destpath = newpath(origpath, destdir)
	print origpath, "->", destpath 

	os.symlink(origpath, destpath)		# choose between the two possibilities
#	shutil.copy(origpath, destpath)	
