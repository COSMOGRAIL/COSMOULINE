import pickle
import datetime
import math
import numpy as np
import sys


def backupfile(filepath, backupdir, code=""):
	"""
	This function backups a file into the backupdir
	and changes the filename to contain the date, time,
	and the "code", if provided.
	"""
	import os
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
	
	print("Backup of %s : %s (%.1f kB)" % (filename, backupfilename, filesize/1024.0))

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def proquest(askquestions):
    """
    Asks the user if he wants to proceed. If not, exits python.
    askquestions is a switch, True or False, that allows to skip the
    questions.
    """
    import sys
    if askquestions:
        answer = input("Tell me, do you want to go on ? (yes/no) ")
        if answer[:3] != "yes":
            sys.exit("Ok, bye.")
        print("")	# to skip one line after the question.


def readimagelist(txtfile):
    """
    Reads a textfile with comments like # and possible blank lines
    Actual data lines look like
    name [possible comment]
    """
    import sys
    import os

    if not os.path.isfile(txtfile):
        print("File does not exist :")
        print(txtfile)
        print("Line format to write : imgname [comment]")
        sys.exit()

    myfile = open(txtfile, "r")
    lines = myfile.readlines()
    myfile.close
    table = []
    for line in lines:
        if line[0] == '#' or len(line) < 4:
            continue

        if len(line.split()) > 1:
            imgname = line.split()[0]
            comment = line.split(None, 1)[1:][0].rstrip('\n')
        else:
            imgname = line.split()[0]
            comment = ""

        # print "imgname :", imgname
        # print "comment :", comment
        table.append([imgname, comment])

    print("I've read", len(table), "images from", txtfile.split("/")[-1])
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
        print("File does not exist :")
        print(mancatfile)
        print("Line format to write : starname xpos ypos [flux]")
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
            print("Format error on line", i+1, "of :")
            print(mancatfile)
            print("We want : starname xpos ypos [flux]")
            sys.exit()
        starid = elements[0]
        xpos = float(elements[1])
        ypos = float(elements[2])
        if nbelements == 4:
            flux = float(elements[3])
        else:
            flux = -1.0
        table.append({"name":starid, "x":xpos, "y":ypos, "flux":flux})

    print("I've read", len(table), "stars from", mancatfile.split("/")[-1])
    return table



# a function to transform an int like 13 into a string like "0013" to use in filenames.
# for the backward transformation, just use int("0013")
def mcsname(i):
    if i >= 10000 or i <= 0:
        raise RuntimeError("MCS filename out of bounds !")
    return "%04i" % int(i)


def writepickle(obj, filepath, verbose=True):
    """
    I write your python object into a pickle file at filepath.
    """
    outputfile = open(filepath, 'wb')
    pickle.dump(obj, outputfile)
    outputfile.close()
    if verbose:
        print("Wrote %s" % filepath)



def readpickle(filepath, verbose=True):
	"""
	I read a pickle file and return whatever object it contains.
	"""
	pkl_file = open(filepath, 'rb')
	obj = pickle.load(pkl_file)
	pkl_file.close()
	if verbose:
		print("Read %s" % filepath)
	return obj


def measure_rms_scatter(mhjds, mags, magerrs, time_chunk=20):
    rms = []
    date = mhjds[0]
    mean_error = []

    while date < mhjds[-1]:
        ind = [i for i,x in enumerate(mhjds) if date < x < date + time_chunk]
        st = np.std(mags[ind])
        rms.append(st)
        mean_error.append(np.mean(magerrs[ind]))
        date += time_chunk


    return rms, mean_error

def juliandate(pythondt):
    """
    Returns the julian date from a python datetime object
    """

    #year = int(year)
    #month = int(month)
    #day = int(day)

    year = int(pythondt.strftime("%Y"))
    month = int(pythondt.strftime("%m"))
    day = int(pythondt.strftime("%d"))

    hours = int(pythondt.strftime("%H"))
    minutes = int(pythondt.strftime("%M"))
    seconds = int(pythondt.strftime("%S"))

    fracday = float(hours + float(minutes)/60.0 + float(seconds)/3600.0)/24.0
    #fracday = 0

    # First method, from the python date module. It was wrong, I had to subtract 0.5 ...
    a = (14 - month)//12
    y = year + 4800 - a
    m = month + 12*a - 3
    jd1 = day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045
    jd1 = jd1 + fracday - 0.5

    # Second method (I think I got this one from Fundamentals of Astronomy)
    # Here the funny -0.5 was part of the game.

    j1 = 367*year - int(7*(year+int((month+9)/12))/4)
    j2 = -int((3*((year + int((month-9)/7))/100+1))/4)
    j3 = int(275*month/9) + day + 1721029 - 0.5
    jd2 = j1 + j2 + j3 + fracday

    #print "Date: %s" % pythondt.strftime("%Y %m %d  %H:%M:%S")
    #print "jd1 : %f" % jd1
    #print "jd2 : %f" % jd2

    # This never happened...
    if abs(jd1 - jd2) > 0.00001:
        print("ERROR : julian dates algorithms do not agree...")
        sys.exit(1)

    return jd2
	

def DateFromJulianDay(JD):
	"""

	Returns the Gregorian calendar
	Based on wikipedia:de and the interweb :-)
	"""

	if JD < 0:
		raise ValueError('Julian Day must be positive')

	dayofwk = int(math.fmod(int(JD + 1.5),7))
	(F, Z) = math.modf(JD + 0.5)
	Z = int(Z)
    
	if JD < 2299160.5:
		A = Z
	else:
		alpha = int((Z - 1867216.25)/36524.25)
		A = Z + 1 + alpha - int(alpha/4)


	B = A + 1524
	C = int((B - 122.1)/365.25)
	D = int(365.25 * C)
	E = int((B - D)/30.6001)

	day = B - D - int(30.6001 * E) + F
	nday = B-D-123
	if nday <= 305:
		dayofyr = nday+60
	else:
		dayofyr = nday-305
	if E < 14:
		month = E - 1
	else:
		month = E - 13

	if month > 2:
		year = C - 4716
	else:
		year = C - 4715

	
	# a leap year?
	leap = 0
	if year % 4 == 0:
		leap = 1
  
	if year % 100 == 0 and year % 400 != 0: 
		print(year % 100, year % 400)
		leap = 0
	if leap and month > 2:
		dayofyr = dayofyr + leap
	
    
	# Convert fractions of a day to time    
	(dfrac, days) = math.modf(day/1.0)
	(hfrac, hours) = math.modf(dfrac * 24.0)
	(mfrac, minutes) = math.modf(hfrac * 60.0)
	seconds = round(mfrac * 60.0) # seconds are rounded
    
	if seconds > 59:
		seconds = 0
		minutes = minutes + 1
	if minutes > 59:
		minutes = 0
		hours = hours + 1
	if hours > 23:
		hours = 0
		days = days + 1

	return datetime.datetime(year,month,int(days),int(hours),int(minutes),int(seconds))

