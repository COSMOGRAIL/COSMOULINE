
import os
import numpy as np
import math
import scipy.signal as signal
import scipy.ndimage as ndimage
import astropy.io.fits as pyfits
import pickle

def backupfile(filepath, backupdir, code=""):
	"""
	This function backups a file into the backupdir
	and changes the filename to contain the date, time,
	and the "code", if provided.
	"""
	import os
	import sys
	import shutil
	import datetime
	import time
	
	now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

	filename = os.path.split(filepath)[-1]
	
	if len(code) == 0:
		backupfilename = now + "_" + filename
	else :
		backupfilename = now + "_" + code + "_" + filename

	#cmd = "cp " + filepath + " " + os.path.join(backupdir, filename)
	#print cmd
	#os.system(cmd)
	
	if not os.path.isdir(backupdir):
		raise RuntimeError("Cannot find the backupdir %s" % backupdir)
	
	shutil.copy(filepath, os.path.join(backupdir, backupfilename))
	
	filesize = os.path.getsize(filepath)
	
	print "Backup of %s : %s (%.1f kB)" % (filename, backupfilename, filesize/1024.0)


def proquest(askquestions):
	"""
	Asks the user if he wants to proceed. If not, exits python.
	askquestions is a switch, True or False, that allows to skip the 
	questions.
	"""
	import sys
	if askquestions:
		answer = raw_input("Tell me, do you want to go on ? (yes/no) ")
		if answer[:3] != "yes":
			sys.exit("Ok, bye.")
		print ""	# to skip one line after the question.


class mterror(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return """
   ______      ___      ___   ____    ____   _  
  |_   _ \   .'   `.  .'   `.|_   \  /   _| | | 
    | |_) | /  .-.  \/  .-.  \ |   \/   |   | | 
    |  __'. | |   | || |   | | | |\  /| |   | | 
   _| |__) |\  `-'  /\  `-'  /_| |_\/_| |_  |_| 
  |_______/  `.___.'  `.___.'|_____||_____| (_) headshot !
      
""" + self.message + "\n"



def readimagelist(txtfile):
	"""
	Reads a textfile with comments like # and possible blank lines
	Actual data lines look like
	name [possible comment]
	"""
	import sys
	import os
	
	if not os.path.isfile(txtfile):
		print "File does not exist :"
		print txtfile
		print "Line format to write : imgname [comment]"
		sys.exit()
	
	myfile = open(txtfile, "r")
	lines = myfile.readlines()
	myfile.close
	table=[]
	for line in lines:
		if line[0] == '#' or len(line) < 4:
			continue
		
		if len(line.split()) > 1:
			imgname = line.split()[0]
			comment = line.split(None, 1)[1:][0].rstrip('\n')
		else:
			imgname = line.split()[0]
			comment = "na"
		
		#print "imgname :", imgname
		#print "comment :", comment
		table.append([imgname, comment])
	
	print "I've read", len(table), "images from", txtfile.split("/")[-1]
	return table


def readmancat(mancatfile):
	"""
	Reads a star catalog written by hand.
	Comment lines start with #, blank lines are ignored.
	The format of an actual data line is
	
	starname xpos ypos [flux]
	
	The data is returned as a list of dicts.
	"""
	import sys
	import os
	
	if not os.path.isfile(mancatfile):
		print "File does not exist :"
		print mancatfile
		print "Line format to write : starname xpos ypos [flux]"
		sys.exit()
	
	myfile = open(mancatfile, "r")
	lines = myfile.readlines()
	myfile.close
	table=[]
	for i, line in enumerate(lines):
		if line[0] == '#' or len(line) < 4:
			continue
		elements = line.split()
		nbelements = len(elements)
		if nbelements != 3 and nbelements != 4:
			print "Format error on line", i+1, "of :"
			print mancatfile
			print "We want : starname xpos ypos [flux]"
			sys.exit()
		starid = elements[0]
		xpos = float(elements[1])
		ypos = float(elements[2])
		if nbelements == 4:
			flux = float(elements[3])
		else:
			flux = -1.0	
		table.append({"name":starid, "x":xpos, "y":ypos, "flux":flux})
	
	print "I've read", len(table), "stars from", mancatfile.split("/")[-1]
	return table


# a little function that might ring a bell...
def notify(computer, withsound, comment="Hmm. Sorry. I kindly ask you to have a look at the screen.", mood="neutral"):
	import os
	import sys
	import commands

	if computer == "maltemac":
		print comment
		if withsound:
			failure, output = commands.getstatusoutput('say "' + comment + '"')
			#os.system('say "' + comment + '"')
		
	elif computer == "obs":
		print comment
		if withsound:
			sys.stdout.write('\a\a\a')
			sys.stdout.flush()
		
	elif computer == "rathna":
		print comment
		if withsound:
			sys.stdout.write('\a\a\a')
			sys.stdout.flush()
		
	elif computer == "topaze":
		print comment
		if withsound:
			sys.stdout.write('\a\a\a')
			sys.stdout.flush()
	else:
		print comment
		if withsound:
			print "(Sorry, nobody told me how to produce a sound on this computer...)"

	# has to be tested :
	# open('/dev/dsp','w').write(''.join(chr(128 * (1 + math.sin(math.pi * 440 * i / 100.0))) for i in xrange(1000)))


# a little function to convert a timedelta object into a string representing a human-readable duration.
def nicetimediff(td):
	from datetime import datetime
	from datetime import timedelta
	
	# could be improved
	strdiff = str(td) # looks like 0:02:04.43353
	
	return strdiff.split(".")[0]
	
	

# a function to transform an int like 13 into a string like "0013" to use in filenames.
# for the backward transformation, just use int("0013")
def mcsname(i):
	if i >= 10000 or i <= 0:
		raise mterror("MCS filename out of bounds !")
	return "%04i"%int(i)
	
	

# pretty self-explanatory : not yet used so much in the pipeline, should be better tested first
# and it turns out that it is mostly completely useless to make true copies instead of links !
# unix : use cp -d to copy while preserving links : standart cp resolves links anyway !!!
def copyorlink(sourcefile, destfile, uselinks=False):
	import shutil
	import os
	if uselinks :
		if os.path.lexists(destfile):
			os.remove(destfile)
		os.symlink(sourcefile, destfile)
	else :
		
		if os.path.lexists(destfile):
			os.remove(destfile)
		shutil.copy(sourcefile, destfile)
		


# Stuff for easy pickling


def writepickle(obj, filepath, verbose=True):

	
	"""
	I write your python object into a pickle file at filepath.
	"""
	outputfile = open(filepath, 'wb')
	pickle.dump(obj, outputfile)
	outputfile.close()
	if verbose:
		print "Wrote %s" % filepath


def readpickle(filepath, verbose=True):
	

	"""
	I read a pickle file and return whatever object it contains.
	"""
	pkl_file = open(filepath, 'rb')
	obj = pickle.load(pkl_file)
	pkl_file.close()
	if verbose:
		print "Read %s" % filepath
	return obj



def makejpgtgz(pngdirpath, tgzdir, maxfilenamelength = 5, askquestions=True):
	"""
	Give me a path to a directory containing png files
	I will transfrom them into jpgs, and then make a tgz archive with these jpgs.
	pngdirpath : the path of the directory that contains the pngs
	tgzdir : the dir in which you want me to put the archive
	maxfilenamelength : used to discriminate between 0001.png and stuff like Mer1_434333_20049874T...
	
	typical use is :
	if makejpgarchives:
		makejpgtgz(pngdir, workdir, askquestions = askquestions)
	"""
	import os
	import glob
	import progressbar
	
	
	pngfiles = sorted(glob.glob(os.path.join(pngdirpath, "*.png")))
	# We get rid of the long filenames (i.e. we only want to process the ordered links like 0001.png etc, not the actual files) :	
	#print pngfiles
	pngfiles = [os.path.basename(pngfile) for pngfile in pngfiles if len(os.path.basename(pngfile)) <= (maxfilenamelength + 4)]
	
	print "I will now make a jpg archive of %i pngs." % len(pngfiles)
	#proquest(askquestions)
	
	#origdir = os.getcwd()
	#os.chdir(pngdirpath)
	
	# We convert them to jpgs :
	
	print "PNG -> JPG conversion ..."
	widgets = [progressbar.Bar('>'), ' ', progressbar.ETA(), ' ', progressbar.ReverseBar('<')]
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(pngfiles)).start()
	for i, pngfile in enumerate(pngfiles):
		cmd = "mogrify -format jpg -quality 100%% %s" % os.path.join(pngdirpath, pngfile)
		pbar.update(i)
		#print cmd
		#print pngfile
		os.system(cmd)
	pbar.finish()
	
	print "Moving files ..."
	origdir = os.getcwd()
	os.chdir(pngdirpath)
	os.mkdir("jpg")
	os.system("mv *.jpg jpg/.")
	
	# We rename this correctly
	if pngdirpath[-1] == "/":
		pngdirpath = pngdirpath[:-1]
	jpgarchivename = os.path.split(pngdirpath)[1] + "_jpg"
	os.system("mv jpg ./%s" % jpgarchivename)
	
	print "Builing archive ..."
	os.system("tar zcvf %s.tgz %s" % (jpgarchivename, jpgarchivename))
	
	print "Moving archive into place ..."
	
	
	os.system("mv %s.tgz %s.tgz" % (jpgarchivename, os.path.join(tgzdir, jpgarchivename)))
	print "Ok, done; the jpg archive is here :"
	print os.path.join(tgzdir, jpgarchivename + ".tgz")
	
	os.chdir(origdir)


# FITS import - export

def fromfits(infilename, hdu = 0, verbose = True):
	"""
	Reads a FITS file and returns a 2D numpy array of the data.
	Use hdu to specify which HDU you want (default = primary = 0)
	"""
	
	pixelarray, hdr = pyfits.getdata(infilename, hdu, header=True,)
	pixelarray = np.asarray(pixelarray).transpose()
	
	pixelarrayshape = pixelarray.shape
	if verbose :
		print "FITS import shape : (%i, %i)" % (pixelarrayshape[0], pixelarrayshape[1])
		print "FITS file BITPIX : %s" % (hdr["BITPIX"])
		print "Internal array type :", pixelarray.dtype.name
	
	return pixelarray, hdr

def tofits(outfilename, pixelarray, hdr = None, verbose = True):
	"""
	Takes a 2D numpy array and write it into a FITS file.
	If you specify a header (pyfits format, as returned by fromfits()) it will be used for the image.
	You can give me boolean numpy arrays, I will convert them into 8 bit integers.
	"""
	pixelarrayshape = pixelarray.shape
	if verbose :
		print "FITS export shape : (%i, %i)" % (pixelarrayshape[0], pixelarrayshape[1])

	if pixelarray.dtype.name == "bool":
		pixelarray = np.cast["uint8"](pixelarray)

	if os.path.isfile(outfilename):
		if verbose:
			print "File exists, I remove it."
		os.remove(outfilename)
	
	if hdr == None: # then a minimal header will be created 
		hdu = pyfits.PrimaryHDU(pixelarray.transpose())
	else: # this if else is probably not needed but anyway ...
		hdu = pyfits.PrimaryHDU(pixelarray.transpose(), hdr)

	hdu.writeto(outfilename)
	
	if verbose :
		print "Wrote %s" % outfilename	



	
