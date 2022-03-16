#
#	In this module we define the functions that know how to read the headers of the various telescopes,
#	and calculate things like dates and exptimes from these headers.
#
#	They return a dict that HAS to match the minimaldbfields defined in addtodatabase.

#	Definition for mjd used in cosmouline is the good and only one : mjd = jd - 2400000.5

# scalefactor of the set is something proportional to a "long range" inverse pixel size : for instance the distance in pixels between two stars stars.
# It will be used for star identification only : no direct impact on the *quality* of the alignment, but could decide on how many stars
# will be used for this alignment ...

# telescopeelevation is in meters, position in deg:min:sec

# gain is in electrons / ADU

# readnoise is in electrons ("per pixel"). At least this is how cosmic.py will use it...

# saturlevel is in ADU (so usually 65000). All scripts that use it will convert it to electrons if required.

import sys
import datetime
import astropy.io.fits as pyfits
import math
import astropy.io.fits as fits

from variousfct import *

print "Re-exec config :"
execfile("../config.py") # yes, this line is required so that settings.py are available within the functions below.


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
		print "ERROR : julian dates algorithms do not agree..."
		sys.exit(1)
	
	return jd2
	

def DateFromJulianDay(JD):
	"""

	Returns the Gregorian calendar
	Based on wikipedia:de and the interweb :-)
	"""

	if JD < 0:
		raise ValueError, 'Julian Day must be positive'

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
		print year % 100, year % 400
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
    



###############################################################################################

# And now the functions that know how to read the headers

###############################################################################################

def eulerc2header(rawimg):
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	pixsize = 0.344
	readnoise = 9.5 # Taken from Christel
	scalingfactor = 0.5612966 # measured scalingfactor (with respect to Mercator = 1.0)
	saturlevel = 65000.0 #arbitrary	

	telescopelongitude = "-70:43:48.00"
	telescopelatitude = "-29:15:24.00"
	telescopeelevation = 2347.0
		
	header = pyfits.getheader(rawimg)
	availablekeywords = header.keys()

	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"
	
	if "DATE-OBS" in availablekeywords: # This should be the default way of doing it.
		pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19], "%Y-%m-%dT%H:%M:%S") # This is the start of the exposure.
	else:
		if "TUNIX_DP" in availablekeywords: # For the very first images
			pythondt = datetime.datetime.utcfromtimestamp(float(header["TUNIX_DP"]))
			print "I have to use TUNIX_DP :", pythondt
			
	if "EXPTIME" in availablekeywords: # Nearly always available.
		exptime = float(header['EXPTIME']) # in seconds.
	elif "TIMEFF" in availablekeywords:
			exptime = float(header['TIMEFF'])
			print "I have to use TIMEFF :", exptime
	else:
		print "WTF ! No exptime !"
		exptime = 360.0
		
	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
	# Now we produce the date and datet fields, middle of exposure :
	
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	
	# We perform some checks with other JD-like header keywords if available :
	if "MJD-OBS" in availablekeywords:
		headermjdfloat = float(header['MJD-OBS']) # should be the middle of exposure, according to hdr comment.
		if abs(headermjdfloat - myownmjdfloat) > 0.0001:
			raise mterror("MJD-OBS disagrees !")
	
	jd = "%.6f" % myownjdfloat 
	mjd = myownmjdfloat
		
	rotator = 0.0
	
	# The gain, we need to read 3 headers.
	# The options are written in order of "trust", the most trusted first.
	gain = 0.0
	if "CCD_SGAI" in availablekeywords: # old images
		gain = float(header['CCD_SGAI'])
		print "Reading gain from CCD_SGAI"
	elif "OGE DET SGAI" in availablekeywords: # intermediary, just after the header format change
		gain = float(header['HIERARCH OGE DET SGAI'])
		print "Reading gain from OGE DET SGAI"
	elif "ESO CAM CCD SGAI" in availablekeywords: # The current format
		gain = float(header['HIERARCH ESO CAM CCD SGAI'])
		print "Reading gain from ESO CAM CCD SGAI"
	elif "ESO CAM2 CCD GAIN" in availablekeywords: # was also used once in the transition phase 04/2009
		gain = float(header["HIERARCH ESO CAM2 CCD GAIN"])
		print "Reading gain from ESO CAM2 CCD GAIN"
	elif "ESO CAM CCD GAIN" in availablekeywords: # was also used once in the transition phase 04/2009
		gain = float(header["HIERARCH ESO CAM CCD GAIN"])
		print "Reading gain from ESO CAM CCD GAIN"
	elif "CCD_FGAI" in availablekeywords: # Very very old ones ... Be careful, this was in ADU/e
		gain = 1.0 / float(header["CCD_FGAI"])
	
	# We do a quick check :
	if gain < 0.5 or gain > 3.0:
		print availablekeywords
		raise mterror("gain = %f ???" % gain)
	
	# The pre-reduction info :
	#preredcomment1 = "None"
	#preredcomment2 = "None"
	#preredfloat1 = 0.0
	#preredfloat2 = 0.0
	preredcomment1 = str(header["PR_NFLAT"])
	preredcomment2 = str(header["PR_NIGHT"])
	preredfloat1 = float(header["PR_FSPAN"])
	preredfloat2 = float(header["PR_FDISP"])
	
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}
	
	return returndict

###############################################################################################

def eulercamheader(rawimg):
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	pixsize = 0.2148 # Measured on an image, Malte
	gain = 2.7 # Rough mean of Monika's measure in Q1, might get updated.
	readnoise = 5.0 # typical value for quadrant 1, i.e. also all LL frames.
	scalingfactor = 0.89767829371 # measured scalingfactor (with respect to Mercator = 1.0)
	saturlevel = 65000.0 # arbitrary
	rotator = 0.0

	telescopelongitude = "-70:43:48.00"
	telescopelatitude = "-29:15:24.00"
	telescopeelevation = 2347.0
		
	header = pyfits.getheader(rawimg)
	#availablekeywords = header.ascardlist().keys() # depreciated, not needed anyway
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"
	
	
	pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19], "%Y-%m-%dT%H:%M:%S") # This is the start of the exposure.
	exptime = float(header['EXPTIME']) # in seconds.
		
	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
	# Now we produce the date and datet fields, middle of exposure :
	
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat
	
	
	# The pre-reduction info :
	# preredcomment1 = "None"
	# preredcomment2 = "None"
	# preredfloat1 = 0.0
	# preredfloat2 = 0.0
	preredcomment1 = str(header["PR_NFLAT"])
	preredcomment2 = str(header["PR_FORMA"]) # There was the "NIGHT" before, but the format is more important.
	if "PR_FSPAN" in header.keys():
		preredfloat1 = float(header["PR_FSPAN"])
	else :
		preredfloat1 = None
	if "PR_FDISP" in header.keys():
		preredfloat2 = float(header["PR_FDISP"])
	else :
		preredfloat2 = None
	
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}
	
	return returndict

###############################################################################################



def mercatorheader(rawimg):
	
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	pixsize = 0.19340976
	gain = 0.93 # e- / ADU, as given by Saskia Prins
	readnoise = 9.5 # ?
	scalingfactor = 1.0 # By definition, others are relative to Mercator.
	saturlevel = 65000.0 # arbitrary	
	
	telescopelongitude = "-17:52:47.99"
	telescopelatitude = "28:45:29.99"
	telescopeelevation = 2327.0
	
	header = pyfits.getheader(rawimg)
	availablekeywords = header.keys()
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"


	if len(header["DATE-OBS"]) >= 19:
		pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19], "%Y-%m-%dT%H:%M:%S")
	
	if len(header["DATE-OBS"]) == 10:
		pythondt = datetime.datetime.utcfromtimestamp(float(header["TUNIX_DP"]))			
		print "Warning : I had to use TUNIX_DP : %s" % pythondt
		print "(But this should be ok)"
	
	exptime = float(header['EXPTIME']) # in seconds.
	
	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
	# Now we produce the date and datet fields, middle of exposure :
	
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	
	# We perform some checks with other JD-like header keywords if available :
	if "MJD" in availablekeywords:
		headermjdfloat = float(header['MJD']) # should be the middle of exposure, according to hdr comment.
		if abs(headermjdfloat - myownmjdfloat) > 0.0001:
			raise mterror("MJD disagrees !")
	
	jd = "%.6f" % myownjdfloat 
	mjd = myownmjdfloat

	
	# Other default values
	rotator = 0.0
	
	# The pre-reduction info :
	preredcomment1 = header["PR_FTYPE"]
	preredcomment2 = header["PR_NIGHT"]
	preredfloat1 = float(header["PR_BIASL"])
	preredfloat2 = float(header["PR_OVERS"])
	
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict


###############################################################################################


def liverpoolheader(rawimg):
	"""
	Reading the header of 2010 RATCam LRT images.
	Probably also ok for previous RATCam images.
	"""
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	#pixsize = 0.279 # (if a 2 x 2 binning is used)
	pixsize = 0.135 # (if a 1 x 1 binning is used, as we do for cosmograil)
	# hmm in the header they give 0.1395 ???
	
	#gain = 0 # We will take it from the header, it's around 2.2, keyword GAIN
	#readnoise = 0.0 # idem, keyword READNOIS, 7.0
	scalingfactor = 1.0 # Not measured : to be done !
	saturlevel = 65000.0 # arbitrary

	telescopelongitude = "-17:52:47.99" # Same location as Mercator ...
	telescopelatitude = "28:45:29.99"
	telescopeelevation = 2327.0
	
	header = pyfits.getheader(rawimg)
	availablekeywords = header.keys()
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	gain = float(header['GAIN'])
	readnoise = float(header['READNOIS'])
	rotator = float(header['ROTSKYPA'])
	
	# Just a test :
	binning = int(header['CCDXBIN'])
	if binning != 1:
		raise mterror("Binning is not 1 x 1 !")
	
	# Now the date and time stuff :
	pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19], "%Y-%m-%dT%H:%M:%S") # beginning of exposure in UTC
	exptime = float(header['EXPTIME'])
	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
	# Now we produce the date and datet fields, middle of exposure :
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt)
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat 
	mjd = myownmjdfloat
	
	# Quick test agains header mjd :
	headermjd = float(header['MJD'])
 	if abs(myownmjdfloat - headermjd) > 0.01: # loose, as we have added exptime/2 ...
 		raise mterror("Header DATE-OBS and MJD disagree !!!")
	
	
	# The pre-reduction info :
	preredcomment1 = "None"
	preredcomment2 = "None"
	preredfloat1 = 0.0
	preredfloat2 = 0.0
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict




###############################################################################################


def maidanaksiteheader(rawimg):
	"""
	Maidanak SITE = raw image format 2030 x 800
	Written 2010 Malte & Denis
	For image prereduced by pypr in 2010
	"""
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	pixsize = 0.266
	gain = 1.16 # From Ildar, to be checked ?
	readnoise = 5.3 # idem
	scalingfactor = 0.723333 #
	saturlevel = 65000.0 # arbitrary
	
	telescopelongitude = "66:53:47.07"
	telescopelatitude = "38:40:23.95"
	telescopeelevation = 2593.0

	header = pyfits.getheader(rawimg)
	availablekeywords = header.keys()
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	rotator = 0.0
	
	# Now the date and time stuff :
	
	if not (len(header["DATE-OBS"]) == 10 and len(header["DATE"]) == 10):
		print "Length error in DATE-OBS and DATE!"
		#raise mterror("Length error in DATE-OBS and DATE")
	if header["DATE-OBS"] != header["DATE"]:
		print "DATE-OBS : %s" % (header["DATE-OBS"])
		print "DATE : %s" % (header["DATE"])
		print "TM_START : %s" % (header["TM_START"])
		#raise mterror("DATE-OBS and DATE do not agree")
	
	pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:10], "%Y-%m-%d")
	pythondt += datetime.timedelta(seconds = header["TM_START"])
	exptime = float(header['EXPTIME'])
	if (exptime < 10.0) or (exptime > 1800):
		print "Exptime : ", exptime
		#raise mterror("Problem with exptime...")
		
	pythondt += datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
	# Now we produce the date and datet fields, middle of exposure :
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt)
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat 
	mjd = myownmjdfloat
	
	# The pre-reduction info :
	preredcomment1 = str(header["PR_NFLAT"])
	preredcomment2 = str(header["PR_NIGHT"])
	preredfloat1 = float(header["PR_FSPAN"])
	preredfloat2 = float(header["PR_FDISP"])
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict


###############################################################################################


def maidanaksiheader(rawimg):
	"""
	Maidanak SI = raw image format 4096 x 4096
	Written 2010 Malte & Gianni
	For image prereduced by pypr in 2010
	"""
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	pixsize = 0.266
	gain = 1.45
	readnoise = 4.7
	scalingfactor = 0.721853 # measured scalingfactor (with respect to Mercator = 1.0)#
	saturlevel = 65000.0 # arbitrary
	
	telescopelongitude = "66:53:47.07"
	telescopelatitude = "38:40:23.95"
	telescopeelevation = 2593.0

	header = pyfits.getheader(rawimg)
	#availablekeywords = header.keys()
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	rotator = 0.0
	
	# Now the date and time stuff :
	
	
	dateobsstring = "%sT%s" % (header["UTDATE"][0:10], header["UTSTART"]) # looks like standart DATE-OBS field
	pythondt = datetime.datetime.strptime(dateobsstring, "%Y-%m-%dT%H:%M:%S") # beginning of exposure in UTC
	exptime = float(header['EXPTIME'])
	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
	if (exptime < 10.0) or (exptime > 1800):
		raise mterror("Problem with exptime...")
		
	# Now we produce the date and datet fields, middle of exposure :
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt)
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat 
	mjd = myownmjdfloat
	
	# The pre-reduction info :
	preredcomment1 = str(header["PR_NFLAT"])
	preredcomment2 = str(header["PR_NIGHT"])
	preredfloat1 = float(header["PR_FSPAN"])
	preredfloat2 = float(header["PR_FDISP"])
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict

###############################################################################################


def maidanak2k2kheader(rawimg):
	"""
	Maidanak 2k2k = raw image format 2084 x 2084
	Written 2012 Malte
	For image prereduced by pypr in 2010
	Those show these ugly "fingers" that we could not remove with the prereduction.
	"""
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	pixsize = 0.4262
	gain = 1.5
	readnoise = 10.0
	scalingfactor = 0.450486 # (with respect to Mercator = 1.0)
	saturlevel = 65000.0 # arbitrary
	
	telescopelongitude = "66:53:47.07"
	telescopelatitude = "38:40:23.95"
	telescopeelevation = 2593.0

	header = pyfits.getheader(rawimg)
	#availablekeywords = header.keys()
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	rotator = 0.0
	
	# Now the date and time stuff :
	
	pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19], "%Y-%m-%dT%H:%M:%S") # beginning of exposure in UTC
	exptime = float(header['EXPTIME'])
	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
	if (exptime < 10.0) or (exptime > 1800):
		raise mterror("Problem with exptime...")
		
	# Now we produce the date and datet fields, middle of exposure :
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt)
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat 
	mjd = myownmjdfloat
	
	# The pre-reduction info :
	preredcomment1 = str(header["PR_NFLAT"])
	preredcomment2 = str(header["PR_NIGHT"])
	preredfloat1 = float(header["PR_FSPAN"])
	preredfloat2 = float(header["PR_FDISP"])
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict


###############################################################################################
def Maidanak_2_5kheader(rawimg):
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

	header = pyfits.getheader(rawimg)

	pixsize = 0.268 #from Otabek and IDlar in 2018
	gain = 1.45  #
	readnoise = 4.7 #
	scalingfactor = 1.0 # measured scalingfactor (with respect to Mercator = 1.0)
	saturlevel = 65535.0  # arbitrary
	rotator = 0.0

	telescopelongitude = "66:53:47.07"
	telescopelatitude = "38:40:23.95"
	telescopeelevation = 2593.0

	# availablekeywords = header.keys() # depreciated, not needed anyway

	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	date_str = header["DATE-OBS"] + 'T' + header['TIME-OBS']

	pythondt = datetime.datetime.strptime(date_str,
										  "%Y-%m-%dT%H:%M:%S")  # This is the start of the exposure.
	exptime = float(header['EXPTIME'])  # in seconds.

	pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt)  # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat

	returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
				  'testcomment': testcomment,
				  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
				  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
				  'mjd': mjd,
				  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
				  'telescopeelevation': telescopeelevation,
				  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
				  'saturlevel': saturlevel
				  }

	return returndict

###############################################################################################

def hctheader(rawimg):
	"""
	HCT : will have to be adapted later so to handle new fields added by pypr prereduction.
	"""
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	pixsize = 0.296
	gain = 0.28 #1.22 old camera
	readnoise = 5.75 #4.8
	scalingfactor = 0.65189 # measured scalingfactor (with respect to Mercator = 1.0)#
	saturlevel = 65000.0 #arbitrary
	
	telescopelongitude = "78:57:50.99"
	telescopelatitude = "32:46:46.00"
	telescopeelevation = 4500.0

	header = pyfits.getheader(rawimg)
	availablekeywords = header.keys()
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	rotator = 0.0
	
	# Now the date and time stuff :
	pythondt = datetime.datetime.strptime(header['DATE-AVG'], "%Y-%m-%dT%H:%M:%S.%f")
	exptime = float(header['EXPTIME'])
	if (exptime < 10.0) or (exptime > 1800):
		raise mterror("Problem with exptime...")
		
	pythondt += datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
	# Now we produce the date and datet fields, middle of exposure :
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt)
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat 
	mjd = myownmjdfloat
	
	# The pre-reduction info :
	#preredcomment1 = str(header["PR_NFLAT"])
	#preredcomment2 = str(header["PR_NIGHT"])
	#preredfloat1 = float(header["PR_FSPAN"])
	#preredfloat2 = float(header["PR_FDISP"])
	
	preredcomment1 = "na"
	preredcomment2 = "na"
	preredfloat1 = 0.0
	preredfloat2 = 0.0
	
	
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict

###############################################################################################

def holiheader(rawimg): # HoLiCam header
	"""
	HoliCam header, adapted together with Dominik Klaes
	"""

	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	pixsize = 0.21 # Holicam, taken from http://www.astro.uni-bonn.de/~ccd/holicam/holicam.htm
	gain = 2.5 # idem 
	readnoise = 9.0 # idem
	scalingfactor = 1.0 # not yet measured ! Do so if required !
	saturlevel = 65000.0 #arbitrary

	telescopelongitude = "6:51:00.00"
	telescopelatitude = "50:09:48.00"
	telescopeelevation = 549.0
	# Images are in natural orientation
	
	header = pyfits.getheader(rawimg)
	# date = str(header['DATE-OBS']) # this does not work for Holicam, funny problem.
	# But there is an alternative : (doesn't work anymore in 2017)
	# headerascardlist = header.cards()
	# headerascardlist["DATE-OBS"].verify("fix")

	#Here is the proper fix :
	hdu = fits.open(rawimg)
	hdu.verify("fix")
	header = hdu[0].header
	date = str(header['DATE-OBS'])
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"
	
	rotator = 0.0

	# Now the date and time stuff :
	pythondt = datetime.datetime.strptime(header['DATE-OBS'], "%Y-%m-%dT%H:%M:%S")
	exptime = float(header['EXPTIME'])
	if (exptime < 10.0) or (exptime > 1800):
		raise mterror("Problem with exptime...")
		
	pythondt += datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
	# Now we produce the date and datet fields, middle of exposure :
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt)
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat 
	mjd = myownmjdfloat
	
	preredcomment1 = "na"
	preredcomment2 = "na"
	preredfloat1 = 0.0
	preredfloat2 = 0.0
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict

###############################################################################################


def smartsandicamheader(rawimg):
	"""
	Malte, Jan 2011
	Info from the web :
	http://www.astronomy.ohio-state.edu/ANDICAM/detectors.html
	Conversion Gain: 2.3 electrons/DN
	Readout Noise: 6.5 electrons (rms)

	0.369 arcsec pixel
	1051x1028 pixels (binned 2x2 w/32 overscan columns):
	BIASSEC  [2:16,2:1025]   ... but we have already cut them anyway, they come prereduced
	DATASEC  [17:1039,1:1026]
	TRIMSEC  [17:1039,2:1025]

	"""
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	pixsize = 0.369
	readnoise = 6.5
	gain = 2.3
	scalingfactor = 0.519995356
	# Measured scalingfactor, done in comparision with Euler (Mercator = 1.0)
	saturlevel = 65000.0

	telescopelongitude = "-70:48:54.00"
	telescopelatitude = "-30:09:54.00"
	telescopeelevation = 2215.0
		
	header = pyfits.getheader(rawimg)
	try:
		availablekeywords = header.keys()
	except:
		availablekeywords = [card[0] for card in header.cards]



	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"
	
	# CAREFUL with these: we fill the header with NA to go on with the deconv...
	
	if "CCDFLTID" not in availablekeywords:
		print "WARNING !!! No CCDFILTID in the headers !!"
		#proquest(askquestions)
		print "You can disable me in /pipe/module/headerstuff line 901"
		
	if "CCDFLTID" in availablekeywords:
		# Quick check of filter :
		if header["CCDFLTID"].strip() != "R":
			print "\n\n\n WARNING : Filter is not R\n\n\n"
	
	if  "JD" in availablekeywords:	
		headerjd = float(header['JD']) # Should be UTC, beginning of exposure
	else:
		print "WARNING !!! No JD in the headers. Going for HJD instead !!"
		#proquest(askquestions)
		headerjd = float(header['HJD'])
		print "You can disable me in /pipe/module/headerstuff line 913"
		
	if "EXPTIME" in availablekeywords:			
		exptime = float(header['EXPTIME']) # in seconds
	else:
		print "WARNING !!! No EXPTIME in the headers. Adding 300[s] as default !!"
		#proquest(askquestions)
		exptime = float(300.0) # in seconds		
		print "You can disable me in /pipe/module/headerstuff line 921"			


	pythondt = DateFromJulianDay(headerjd)	
	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
	# Now we produce the date and datet fields, middle of exposure :
	
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5 # modified Julian days
	jd = "%.6f" % myownjdfloat 
	mjd = myownmjdfloat
		
	rotator = 0.0
	preredcomment1 = ""
	preredcomment2 = ""
	preredfloat1 = 0.0
	preredfloat2 = 0.0
	
	if "CCDFILTID" in availablekeywords:
		preredcomment2 = "Header CCDFILTID = %s" % header["CCDFILTID"]
	if "TIME-OBS" in availablekeywords:
		preredcomment1 = "Header TIME-OBS = %s" % header['TIME-OBS'] 
	if "HJD" in availablekeywords:
		preredfloat1 = float(header['HJD'])
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}
	
	return returndict





###############################################################################################



def skysimheader(rawimg):

    """
    skysim = skymaker simulated images
    Written 2010 Gianni
    """
	
    print rawimg
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
    header = pyfits.getheader(rawimg)
    availablekeywords = header.keys()


    pixsize = float(header['PIXSIZE'])
    gain = float(header['GAIN'])
    readnoise = float(header['RON'])
    scalingfactor = 1.0
    saturlevel = 65000.0 # arbitrary
	
    telescopelongitude = "00:00:00.00"
    telescopelatitude = "00:00:00.00"
    telescopeelevation = 0.0
	
    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    rotator = 0.0


    dateobsstring = "%s" % (header["DATE-OBS"]) # looks like standart DATE-OBS field
    pythondt = datetime.datetime.strptime(dateobsstring, "%Y-%m-%dT%H%M%S") # beginning of exposure in UTC
    exptime = float(header['EXPOTIME'])
    pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
    if (exptime < 10.0) or (exptime > 1800):
        raise mterror("Problem with exptime...")
	
	
    # Now we produce the date and datet fields, middle of exposure :
    date = pythondt.strftime("%Y-%m-%d")
    datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")


    myownjdfloat = juliandate(pythondt)
    myownmjdfloat = myownjdfloat - 2400000.5
    jd = "%.6f" % myownjdfloat 
    mjd = myownmjdfloat
	
	
    # The pre-reduction info :
    preredcomment1 = "None"
    preredcomment2 = "None"
    preredfloat1 = 0.0
    preredfloat2 = 0.0
	
    # We return a dictionnary containing all this info, that is ready to be inserted into the database.
    returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
    'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
    'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
    'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
    'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
    'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
    }

    return returndict


###############################################################################################

def PANSTARRSheader(rawimg):
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

	header = pyfits.getheader(rawimg)

	pixsize = 0.26 # Measured on an image, Malte
	gain = float(header['CELL.GAIN'])  # Rough mean of Monika's measure in Q1, might get updated.
	readnoise = float(header['CELL.READNOISE']) # typical value for quadrant 1, i.e. also all LL frames.
	scalingfactor = 0.89767829371  # measured scalingfactor (with respect to Mercator = 1.0)
	saturlevel = float(header['CELL.SATURATION'])  # arbitrary
	rotator = 0.0

	telescopelongitude = "-156:15:26.00"
	telescopelatitude = "20:42:30.00"
	telescopeelevation = 3048.0

	# availablekeywords = header.keys() # depreciated, not needed anyway

	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	pythondt = datetime.datetime.strptime(header["DATE"][0:19],
										  "%Y-%m-%dT%H:%M:%S")  # This is the start of the exposure.
	exptime = float(header['EXPTIME'])  # in seconds.

	pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt)  # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat

	# The pre-reduction info :
	# preredcomment1 = "None"
	# preredcomment2 = "None"
	# preredfloat1 = 0.0
	# preredfloat2 = 0.0
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
				  'testcomment': testcomment,
				  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
				  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
				  'mjd': mjd,
				  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
				  'telescopeelevation': telescopeelevation,
				  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
				  'saturlevel': saturlevel
				  }

	return returndict

#########################################################################################################
def SPECULOOSheader(rawimg):
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

	header = pyfits.getheader(rawimg)

	pixsize = 0.347 # Measured on an image, Malte
	gain = 1.0  # Rough mean of Monika's measure in Q1, might get updated.
	readnoise = 10.0 # typical value for quadrant 1, i.e. also all LL frames.
	scalingfactor = 1.0 # measured scalingfactor (with respect to Mercator = 1.0)
	saturlevel = 65535.0  # arbitrary
	rotator = 0.0

	telescopelongitude = "-24:36:58"
	telescopelatitude = "-70:23:26"
	telescopeelevation = 2482.0

	# availablekeywords = header.keys() # depreciated, not needed anyway

	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19],
										  "%Y-%m-%dT%H:%M:%S")  # This is the start of the exposure.
	exptime = float(header['EXPTIME'])  # in seconds.

	pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt)  # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat

	returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
				  'testcomment': testcomment,
				  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
				  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
				  'mjd': mjd,
				  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
				  'telescopeelevation': telescopeelevation,
				  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
				  'saturlevel': saturlevel
				  }

	return returndict

#########################################################################################################

def UH2m2header(rawimg):
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

	header = pyfits.getheader(rawimg)

	pixsize = 0.22 # Measured on an image, Malte
	gain = 1.78  #
	readnoise = 10.0 # t
	scalingfactor = 1.0 # measured scalingfactor (with respect to Mercator = 1.0)
	saturlevel = 65535.0  # arbitrary
	rotator = 0.0

	telescopelongitude = "19:49:34"
	telescopelatitude = "-155:28:15"
	telescopeelevation = 4205.0

	# availablekeywords = header.keys() # depreciated, not needed anyway

	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	date_str = header["DATE-OBS"] + 'T' + header['UT'][1:-3]

	pythondt = datetime.datetime.strptime(date_str,
										  "%Y-%m-%dT%H:%M:%S")  # This is the start of the exposure.
	exptime = float(header['EXPTIME'])  # in seconds.

	pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt)  # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat

	returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
				  'testcomment': testcomment,
				  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
				  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
				  'mjd': mjd,
				  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
				  'telescopeelevation': telescopeelevation,
				  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
				  'saturlevel': saturlevel
				  }

	return returndict

#########################################################################################################

def combiheader(rawimg):
	"""
	combi = it is not a telscope. This is use to read the header of the combined images and to add them to the database like a new telescope.
	Written 2010 Denis
	For image combined by night of observation.
	"""
	print rawimg

	header = pyfits.getheader(rawimg)
	availablekeywords = header.keys()
	
	imgname = setname + "_" + header["IMGNAME"]
	
	pixsize = float(header["PIXSIZE"])
	gain = float(header["GAIN"])
	readnoise = float(header["RDNOISE"])
	scalingfactor = float(header["SCFACTOR"]) # measured scalingfactor (with respect to Mercator = 1.0)#
	saturlevel = float(header["SATURLVL"])
	
	combinum = int(header["COMBINUM"])
	combinumname = combidirname + '_num'
	
	telescopelongitude = str(header["TELSLON"])
	telescopelatitude = str(header["TELSLAT"])
	telescopeelevation = 2000.0 	#float(header["TELSELE"])
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	rotator = 0.0
	
	# Now the date and time stuff :
	
	jdfloat = float(header["JD"])
	
	pythondt = DateFromJulianDay(jdfloat)
	jd = "%.6f" %jdfloat
	exptime = float(header['EXPTIME'])
	
	
	if (exptime < 10.0) or (exptime > 7200):
		print "Exptime : ", exptime
		raise mterror("Problem with exptime...")
		
	# Now we produce the date and datet fields, middle of exposure :
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownmjdfloat = jdfloat - 2400000.5 
	mjd = myownmjdfloat
	
	# The pre-reduction info :
	preredcomment1 = "combined"
	preredcomment2 = "None"
	preredfloat1 = float(header["NCOMBINE"])
	preredfloat2 = 0.0
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, combinumname: combinum,'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict
	
	

##############################################################################################################

def fors2header(rawimg):
	"""
	Version for VLT images
	Experimental
	Written by Vivien, 01.2015
	"""
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension

	# From FORS2 User Manual

	pixsize = 0.126 # from header. 0.25 indicated in fors2 manual
	gain = 0.806 # http://www.eso.org/observing/dfo/quality/FORS2/reports/HEALTH/trend_report_CONAD_HC.html. INVERSE OF CONV. FACTOR
		# possible values
		# 0.8 # from headers of CHIP1 / CHIP2
	readnoise = 2.62 # taken from http://www.eso.org/observing/dfo/quality/FORS2/reports/HEALTH/trend_report_BIAS_ron_raw_HC.html
		# possible values:
		# 2.7 # from header of CHIP1
		# 2.62 # taken from http://www.eso.org/observing/dfo/quality/FORS2/reports/HEALTH/trend_report_BIAS_ron_raw_HC.html
		# 3.6 # from header of CHIP2
	scalingfactor = 1.0 # no need for it right now...
	saturlevel = 65000.0 # still arbitrary
	rotator = 0.0 # ??

	telescopelongitude = "-70:24:11.642"
	telescopelatitude = "-24:37:33.117"
	telescopeelevation = 2635.43

	header = pyfits.getheader(rawimg)
	# availablekeywords = header.keys()  # not used anyway

	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19], "%Y-%m-%dT%H:%M:%S") # This is the start of the exposure.
	exptime = float(header['EXPTIME']) # in seconds.

	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat


	# The pre-reduction info :
	# May be useful one day...can be used.
	preredcomment1 = "None"
	preredcomment2 = "None"
	preredfloat1 = 0.0
	preredfloat2 = 0.0


	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg,
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict


##############################################################################################################


def efosc2header(rawimg):
	"""
	Version for NTT's EFOSC2 images
	Experimental
	Written by Vivien, 01.2016
	"""
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension

	# From EFOSC2 User Manual and http://www.eso.org/sci/facilities/lasilla/instruments/efosc/inst/Ccd40.html
	pixsize = 0.24  # 0.12 for 1x1 binning
	gain = 1.34  # varies between 1.31 and 1.34...
	readnoise = 9.8  # varies between 8.5 and 9.8
	scalingfactor = 1.0  # no need for it right now...
	saturlevel = 65535.0  # in ADU
	rotator = 0.0  # ??

	telescopelongitude = "-70:44:01.50"
	telescopelatitude = "-29:15:32.10"
	telescopeelevation = 2375.0

	header = pyfits.getheader(rawimg)
	# availablekeywords = header.keys()  # not used anyway

	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19], "%Y-%m-%dT%H:%M:%S") # This is the start of the exposure.
	exptime = float(header['EXPTIME']) # in seconds.

	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat


	# The pre-reduction info :
	# May be useful one day...can be used.
	preredcomment1 = "None"
	preredcomment2 = "None"
	preredfloat1 = 0.0
	preredfloat2 = 0.0


	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg,
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict

##############################################################################################################


def wfiheader(rawimg):
	"""
	Version for 2.2m WFI images
	Experimental
	Written by Vivien, 02.2016
	"""
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension

	# From WFI User Manual
	pixsize = 0.238  # 0.12 for 1x1 binning
	gain = 2.0  # varies between 1.31 and 1.34...
	readnoise = 4.5  # varies between 8.5 and 9.8
	scalingfactor = 1.0  # no need for it right now...
	saturlevel = 65535.0  # in ADU
	rotator = 0.0  # ??

	telescopelongitude = "-70:44:04.543"
	telescopelatitude = "-29:15:15.433"
	telescopeelevation = 2335.0

	header = pyfits.getheader(rawimg)
	# availablekeywords = header.keys()  # not used anyway

	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19], "%Y-%m-%dT%H:%M:%S") # This is the start of the exposure.
	exptime = float(header['EXPTIME']) # in seconds.

	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat


	# The pre-reduction info :
	# May be useful one day...can be used.
	preredcomment1 = "None"
	preredcomment2 = "None"
	preredfloat1 = 0.0
	preredfloat2 = 0.0


	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg,
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict


##############################################################################################################


def grondheader(rawimg):
	"""
	Version for 2.2m GROND images
	Experimental
	Written by Vivien, 02.2016
	"""
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension

	# From headers, http://www.mpe.mpg.de/~jcg/GROND/grond_pasp.pdf and the web...
	pixsize = 0.158  #

	readnoise = 5.0  # 5 for slow mode, 23 for fast mode. Let's assume slow mode here...
	scalingfactor = 1.0  # no need for it right now...
	saturlevel = 65535.0  # in ADU
	rotator = 0.0  # ??

	telescopelongitude = "-70:44:04.543"
	telescopelatitude = "-29:15:15.433"
	telescopeelevation = 2335.0

	header = pyfits.getheader(rawimg)
	# availablekeywords = header.keys()  # not used anyway
	gain = header["GAIN"]  # put it at 1.0 for now, according to the header...
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	pythondt = datetime.datetime.strptime(header["DATE"][0:19], "%Y-%m-%dT%H:%M:%S") # This is the start of the exposure.
	exptime = float(header['TEXPTIME']) # in seconds. exptime is 1 for all images...

	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat


	# The pre-reduction info :
	# May be useful one day...can be used.
	preredcomment1 = "None"
	preredcomment2 = "None"
	preredfloat1 = 0.0
	preredfloat2 = 0.0


	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg,
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict


##############################################################################################################


def gmosheader(rawimg):
	"""
	Version for 6.5m GMOS-S images
	Experimental
	Written by Vivien, 06.2017
	"""
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	header = pyfits.getheader(rawimg)

	# From headers, http://www.gemini.edu/sciops/instruments/gmos/imaging/camera-properties and the web...
	pixsize = header["PIXSCALE"]  #

	readnoise = header["RDNOISE"]  # 5 for slow mode, 23 for fast mode. Let's assume slow mode here...
	scalingfactor = 1.0  # no need for it right now...
	saturlevel = 125000.0  # in ADU
	rotator = 0.0  # ??

	telescopelongitude = "-70:44:12.096"
	telescopelatitude = "-30:14:26.700"
	telescopeelevation = 2722.0


	# availablekeywords = header.keys()  # not used anyway
	gain = header["GAIN"]  # put it at 1.0 for now, according to the header...
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	pythondt = datetime.datetime.strptime(header["DATE"][0:19], "%Y-%m-%dT%H:%M:%S") # This is the start of the exposure.
	exptime = float(header['EXPTIME']) # in seconds.

	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat


	# The pre-reduction info :
	# May be useful one day...can be used.
	preredcomment1 = "None"
	preredcomment2 = "None"
	preredfloat1 = 0.0
	preredfloat2 = 0.0


	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg,
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict


##############################################################################################################


def sdssheader(rawimg):
	"""
	Version for SDSS images
	Experimental
	Written by Vivien, 07.2016
	some infos from here:

	https://www.sdss3.org/instruments/camera.php
	https://www.sdss3.org/dr8/algorithms/magnitudes.php#nmgy
	http://iopscience.iop.org/article/10.1086/500975/pdf

	counts units seems to be nanomaggies

	"""
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension

	pixsize = 0.396  #

	readnoise = 5.0  # 5 for slow mode, 23 for fast mode. Let's assume slow mode here...
	scalingfactor = 1.0  # no need for it right now...
	saturlevel = 65535.0  # in ADU
	rotator = 0.0  # ??

	telescopelongitude = "-105:49:13.50"
	telescopelatitude = "+32:46:49.30"
	telescopeelevation = 2788.0

	header = pyfits.getheader(rawimg)
	# availablekeywords = header.keys()  # not used anyway
	gain = 1.0  # put it at 1.0 for now, according to the header...
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"


	pythondt = datetime.datetime.strptime(header["DATE-OBS"]+"T"+header["TAIHMS"][:-3], "%Y-%m-%dT%H:%M:%S") # This is the start of the exposure.
	exptime = float(header['EXPTIME']) # in seconds.

	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat


	# The pre-reduction info :
	# May be useful one day...can be used.
	preredcomment1 = "None"
	preredcomment2 = "None"
	preredfloat1 = 0.0
	preredfloat2 = 0.0


	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg,
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict


###############################################################################################


def noheader(rawimg):
	
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	pixsize = 1.0
	gain = 1.0
	readnoise = 5.0
	scalingfactor = 1.0
	saturlevel = 65000.0 #arbitrary
	
	telescopelongitude = "00:00:00.00"
	telescopelatitude = "00:00:00.00"
	telescopeelevation = 0.0
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"
	
	pythondt = datetime.datetime.strptime("2002-10-10T13:37:00", "%Y-%m-%dT%H:%M:%S") # 2000-00-00 was not working...
	exptime = 300.0
	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.
	
	# Now we produce the date and datet fields, middle of exposure :
	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt)
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat 
	mjd = myownmjdfloat
	
	# Other default values
	rotator = 0.0
	
	# The pre-reduction info :
	preredcomment1 = "None"
	preredcomment2 = "None"
	preredfloat1 = 0.0
	preredfloat2 = 0.0
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg, 
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict



###############################################################################################

def VSTheader(rawimg):
	"""
	Version for VST images
	Experimental
	"""
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension

	header = pyfits.getheader(rawimg)
	pixsize = 0.215
	gain = header['GAIN']
	print "image : %s, gain : %2.4f"%(imgname, gain)
	readnoise = 2.1  # from the Health check report in May 2019
	scalingfactor = 1.0  # no need for it right now...
	saturlevel = header['SATLEVEL']  # in ADU
	rotator = 0.0  # useless

	telescopelongitude = "-70:24:10.19"
	telescopelatitude = "-24:37:22.79" #paranal
	telescopeelevation = 2635.0

	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	pythondt = datetime.datetime.strptime(header["OBSTART"], "%Y-%m-%dT%H:%M:%S") # This is the start of the exposure.
	exptime = float(header['EXPTIME']) # in seconds.

	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat


	# The pre-reduction info :
	# May be useful one day...can be used.
	preredcomment1 = "Zero Point"
	preredcomment2 = "None"
	preredfloat1 = header['ZP']
	preredfloat2 = 0.0


	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg,
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict

def VATTheader(rawimg):
	"""
	Version for VATT images
	Written by Martin, 09.2019
	"""
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension

	header = pyfits.getheader(rawimg)
	pixsize = 0.187
	gain = 1.730
	print "image : %s, gain : %2.4f"%(imgname, gain)
	readnoise = 5.1  # from the http://www.public.asu.edu/~rjansen/vatt/vatt4k.html
	scalingfactor = 1.0  # no need for it right now...
	saturlevel = 65535.0  # in ADU
	rotator = 0.0  # useless

	telescopelongitude = "-109:53:31.00"
	telescopelatitude = "32:42:05.00" #MT Graham, AZ
	telescopeelevation = 3178.0

	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	pythondt = datetime.datetime.strptime(header["DATE-OBS"]+"T"+header["TIME-OBS"][:-4], "%Y-%m-%dT%H:%M:%S") # This is the start of the exposure.
	exptime = float(header['EXPTIME']) # in seconds.

	pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.

	# Now we produce the date and datet fields, middle of exposure :

	date = pythondt.strftime("%Y-%m-%d")
	datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

	myownjdfloat = juliandate(pythondt) # The function from headerstuff.py
	myownmjdfloat = myownjdfloat - 2400000.5
	jd = "%.6f" % myownjdfloat
	mjd = myownmjdfloat


	# The pre-reduction info :
	# May be useful one day...can be used.
	preredcomment1 = "None"
	preredcomment2 = "None"
	preredfloat1 = 0.0
	preredfloat2 = 0.0


	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,'testcomment':testcomment ,
	'telescopename':telescopename, 'setname':setname, 'rawimg':rawimg,
	'scalingfactor':scalingfactor, 'pixsize':pixsize, 'date':date, 'datet':datet, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain, 'readnoise':readnoise, 'rotator':rotator, 'saturlevel':saturlevel,
	'preredcomment1':preredcomment1, 'preredcomment2':preredcomment2, 'preredfloat1':preredfloat1, 'preredfloat2':preredfloat2
	}

	return returndict
"""
if telescopename == "Liverpool":
	#pixsize = 0.279 # (if a 2 x 2 binning is used)
	pixsize = 0.135 # (if a 1 x 1 binning is used, as we do for cosmograil)
	gain = 0 # We will take it from the header, it's around 2.2, keyword GAIN
	readnoise = 0.0 # idem, keyword READNOIS, 7.0
	scalingfactor = 1.0 # Not measured : to be done !

	telescopelongitude = "-17:52:47.99" # Same location then Mercator ...
	telescopelatitude = "28:45:29.99"
	telescopeelevation = 2327.0
	
	# To put images into natural orientation : invert X and rotate 270
	

if telescopename == "MaidanakSITE":	# MaidanakSITE = Maidanak nitrogen cooled camera
	pixsize = 0.266
	gain = 1.16
	readnoise = 5.3
	scalingfactor = 0.723333 # measured scalingfactor (with respect to Mercator = 1.0)
	
	telescopelongitude = "66:53:47.07"
	telescopelatitude = "38:40:23.95"
	telescopeelevation = 2593.0


if telescopename == "MaidanakSI":	# MaidanakSI = korean 4k x 4k CCD
	pixsize = 0.266			# yes, it's the same pixel size as SITE
	gain = 1.45
	readnoise = 4.7
	scalingfactor = 0.721853 # measured scalingfactor (with respect to Mercator = 1.0)
	
	telescopelongitude = "66:53:47.07"
	telescopelatitude = "38:40:23.95"
	telescopeelevation = 2593.0


if telescopename == "MaidanakPeltier":	# Maidanak Peltier cooled CCD (something like a SBIG)
	pixsize = 0.43025		# quick and dirty, from measured scalingfactor
	gain = 1.4
	readnoise = 5.0
	scalingfactor = 0.449525 # measured scalingfactor (with respect to Mercator = 1.0)
	
	telescopelongitude = "66:53:47.07"
	telescopelatitude = "38:40:23.95"
	telescopeelevation = 2593.0

"""

"""
if telescopename == "HCT":
	pixsize = 0.296
	gain = 1.22
	readnoise = 4.7
	scalingfactor = 0.65189
	
	telescopelongitude = "78:57:50.99"
	telescopelatitude = "32:46:46.00"
	telescopeelevation = 4500.0


if telescopename == "NOTalfosc":
	pixsize = 0.188 # was written somewhere in one header
	gain = 1.5 # this is unknown, I have no idea
	readnoise = 5.0	# same remark
	scalingfactor = 1.01516 # measured, with respect to mercator = 1.0

	
	telescopelongitude = "-17:52:47.99"
	telescopelatitude = "28:45:29.99"
	telescopeelevation = 2327.0


if telescopename == "HoLi":
	pixsize = 0.21 # Holicam, taken from http://www.astro.uni-bonn.de/~ccd/holicam/holicam.htm
	gain = 2.5 # idem 
	readnoise = 9.0 # idem
	scalingfactor = 1.0 # not yet measured ! Do so  !

	telescopelongitude = "6:51:00.00"
	telescopelatitude = "50:09:48.00"
	telescopeelevation = 549.0
	# Images are in natural orientation



if telescopename == "NOHEADER":
	pixsize = 0.126
	gain = 1.0
	readnoise = 10.0
	scalingfactor = 1.0

	telescopelongitude = "00:00:00.00"
	telescopelatitude = "00:00:00.00"
	telescopeelevation = 0.0
	


def liverpoolheader(rawimg):
	print rawimg
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	header = pyfits.getheader(rawimg)
	
	# telescopename, setname, scalingfactor, pixsize
	# are known (global)
	gain = float(header['GAIN'])
	readnoise = float(header['READNOIS'])
	
	binning = int(header['CCDXBIN'])
	if binning != 2:
		raise mterror("Binning is not 2 x 2 !")
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	exptime = float(header['EXPTIME'])
	date = str(header['DATE']) # This is in UTC, format like 2008-04-11
	# JD does not exist, so we calculate it from the 
	
	dateobs = str(header['DATE-OBS']) # beginning of exp in UTC
	d = dateobs[0:10] # should be the same then DATE
	if d != date:
		raise mterror("DATE-OBS and DATE disagree ! %s %s" % (d, date))
	h = int(dateobs[11:13])
	m = int(dateobs[14:16])
	s = int(dateobs[17:19])
	
	utcent = exptime/2 + s + 60*m + 3600*h
	jd = str(chandrajuliandate(d, utcent))
	
	mjd = float(header['MJD'])
	if abs(float(jd) - 2400000.5 - mjd) > 0.01: # loose, as we have added exptime/2 ...
		print "mjd -> %f" % (mjd + 2400000.5)
		print "jd  -> %s" % jd
		raise mterror("WARNING : header JD and MJD disagree !!!")
	
	rotator = float(header['ROTSKYPA'])
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,
	'testcomment':testcomment ,'telescopename':telescopename, 'setname':setname,
	'rawimg':rawimg, 'scalingfactor':scalingfactor, 'pixsize':pixsize,
	'date':date, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain,
	'readnoise':readnoise, 'rotator':rotator}
	
	return returndict


def hctheader(rawimg): # and for the chandra telescope
	print rawimg
	
	imgname = setname + "_" + rawimg.split("/")[-1].split(".")[0] # drop extension
	
	header = pyfits.getheader(rawimg)
	
	# telescopename, setname, scalingfactor, pixsize
	# are known (global)
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	date = header['DATE-OBS'] # format like 2008-04-11
	#print date
	exptime = float(header['EXPTIME'])
	#print exptime
	
	gaintext = str(header['GAINM'])
	if gaintext != "HIGH":
		raise mterror("Unknown GAINM")
	
	utstart = int(header['TM_START'])
	utend = int(header['TM_END'])
	#print utstart
	#print utend
	if (utend - utstart) > 600:
		raise mterror("Oh boy, error 58877HGY8")
	utcent = (utstart + exptime/2.0)
	
	jd = chandrajuliandate(date, utcent)
	mjd = jd - 2400000.5 
	jd = "%.10f" % jd # convert to string
	
	rotator = 0.0
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,
	'testcomment':testcomment ,'telescopename':telescopename, 'setname':setname,
	'rawimg':rawimg, 'scalingfactor':scalingfactor, 'pixsize':pixsize,
	'date':date, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain,
	'readnoise':readnoise, 'rotator':rotator}
	
	return returndict


def koreanheader(rawimg): # this reads the korean 4k by 4k camera files from Maidanak
	print rawimg
	
	imgname = setname + "_" + rawimg.split("/")[-1].split(".")[0] # drop extension
	header = pyfits.getheader(rawimg)
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	date = header['UTDATE'] # format like 2008-04-11
	#print date
	exptime = float(header['EXPTIME']) # this is in seconds
	#print exptime
	utstart = header['UTSTART'] 	# this is a sting like '18:37:51'
	# convert this to the utcent of Chandra, and then use the same fct to calc JD.
	uthour = int(utstart.split(':')[0])
	utmin = int(utstart.split(':')[1])
	utsec = int(utstart.split(':')[2])

	utcent = uthour*3600. + utmin*60. + utsec + exptime/2.0

	jd = chandrajuliandate(date, utcent)
	mjd = jd - 2400000.5 
	jd = "%.10f" % jd # convert to string
	# mjd = "%.10f" % mjd # NO, as we keep mjd as a float now.
	
	rotator = 0.0
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,
	'testcomment':testcomment ,'telescopename':telescopename, 'setname':setname,
	'rawimg':rawimg, 'scalingfactor':scalingfactor, 'pixsize':pixsize,
	'date':date, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain,
	'readnoise':readnoise, 'rotator':rotator}
	
	return returndict

def peltierheader(rawimg): # this reads the peltier-cooled camera files from Maidanak
	print rawimg
	
	imgname = setname + "_" + rawimg.split("/")[-1].split(".")[0] # drop extension
	header = pyfits.getheader(rawimg)
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	longdate = header['DATE-OBS'] # format like 2008-02-24T20:14:15.422 in UTC
	date = longdate.split('T')[0]
	#print date
	
	exptime = float(header['EXPTIME']) # this is in seconds
	
	utstart = longdate.split('T')[1] # this is a sting like '18:37:51.346'

	uthour = float(utstart.split(':')[0])
	utmin = float(utstart.split(':')[1])
	utsec = float(utstart.split(':')[2])
	utcent = uthour*3600. + utmin*60. + utsec + exptime/2.0

	jd = chandrajuliandate(date, utcent)
	mjd = jd - 2400000.5 
	jd = "%.10f" % jd # convert to string
	#mjd = "%.10f" % mjd # NO, as we keep mjd as a float now.
	
	rotator = 0.0
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,
	'testcomment':testcomment ,'telescopename':telescopename, 'setname':setname,
	'rawimg':rawimg, 'scalingfactor':scalingfactor, 'pixsize':pixsize,
	'date':date, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain,
	'readnoise':readnoise, 'rotator':rotator}
	
	return returndict

def notalfoscheader(rawimg): # NOT ALFOSC camera
	print rawimg
	
	imgname = setname + "_" + rawimg.split("/")[-1].split(".")[0] # drop extension
	
	header = pyfits.getheader(rawimg)
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	date = header['DATE-OBS'][:10] # format like 2008-04-11, it's the end of the observation
					# we need this [:10], sometimes there is also the time given...
	print date
	exptime = float(header['EXPTIME'])
	print exptime
	
	#gaintext = str(header['GAINMODE'])		# cannot use this, it's not in every header...
	#if gaintext != "HIGH":
	#		raise mterror("Unknown GAINM")
	
	utstart = int(header['TM_START'])
	utend = int(header['TM_END'])
	print utstart
	print utend
	if abs(utend - utstart) > 600:
		raise mterror("Oh boy, error 58877HGY8")
	utcent = (utstart + exptime/2.0)
	
	jd = chandrajuliandate(date, utcent)
	# we perform a quick test to compare with the original JD :
	
	if "JD" in header:
		headerjd = header["JD"]
		if abs(jd - headerjd) > 0.01:
			raise mterror("JD disagree")
	
	mjd = jd - 2400000.5 
	jd = "%.10f" % jd # convert to string
	
	rotator = 0.0
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,
	'testcomment':testcomment ,'telescopename':telescopename, 'setname':setname,
	'rawimg':rawimg, 'scalingfactor':scalingfactor, 'pixsize':pixsize,
	'date':date, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain,
	'readnoise':readnoise, 'rotator':rotator}
	
	return returndict

def holiheader(rawimg): # HoLiCam header
	print rawimg
	
	imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0] # drop extension
	
	header = pyfits.getheader(rawimg)
	
	# telescopename, setname, scalingfactor, pixsize
	# are known (global)
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	#date = str(header['DATE-OBS']) # this does not work for Holicam, funny problem.
	# But there is an alternative :
	headerascardlist = header.ascardlist()
	headerascardlist["DATE-OBS"].verify("fix")
	date = headerascardlist["DATE-OBS"].value[0:10]
	
	mjd = float(header['MJD'])
	jd = mjd + 2400000.5
	jd = "%.10f" % jd # convert to string

	exptime = float(header['EXPTIME'])
		
	rotator = 0.0
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,
	'testcomment':testcomment ,'telescopename':telescopename, 'setname':setname,
	'rawimg':rawimg, 'scalingfactor':scalingfactor, 'pixsize':pixsize,
	'date':date, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain,
	'readnoise':readnoise, 'rotator':rotator}
	
	return returndict

def noheader(rawimg):	# We do not read the header, only return default values...
	print "No header from", rawimg
	
	imgname = setname + "_" + rawimg.split("/")[-1].split(".")[0] # drop extension
	
	treatme = True
	gogogo = True
	whynot = "na"
	testlist = False
	testcomment = "na"

	longdate = "0000-00-00T00:00:00.0000" # format like 2008-02-24T20:14:15.422 in UTC
	print longdate
	date = longdate.split('T')[0]
	
	exptime = 123.45 # this is in seconds
	
	jd = 2400000.5	# mjd will be 0.0 !
	mjd = jd - 2400000.5 
	jd = "%.10f" % jd # convert to string
	
	rotator = 0.0
	
	# We return a dictionnary containing all this info, that is ready to be inserted into the database.
	
	returndict = {'imgname':imgname, 'treatme':treatme, 'gogogo':gogogo, 'whynot':whynot, 'testlist':testlist,
	'testcomment':testcomment ,'telescopename':telescopename, 'setname':setname,
	'rawimg':rawimg, 'scalingfactor':scalingfactor, 'pixsize':pixsize,
	'date':date, 'jd':jd, 'mjd':mjd,
	'telescopelongitude':telescopelongitude, 'telescopelatitude':telescopelatitude, 'telescopeelevation':telescopeelevation,
	'exptime':exptime, 'gain':gain,
	'readnoise':readnoise, 'rotator':rotator}
	
	return returndict
"""



###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################














###############################################################################################


# Should not be used anymore, refer to the function juliandate.
"""
def chandrajuliandate(date, utcent):
	#Calculates the julian date from 
	#- date : yyyy-mm-dd
	#- utcent : number of seconds since 0:00
	
	import time
	import sys
	#import math
	
	if len(date.split('-')) != 3:
		print "Huge problem  !"
		sys.exit()
		 
	(year, month, day) = date.split('-')
	year = int(year)
	month = int(month)
	day = int(day)
	
	#hours = utcent / 3600.0
	#hour = int(math.floor(hours))
	#inutes = (hours - hour)*60.0
	#minute = int(math.floor(minutes))
	#seconds = (minutes-minute)*60.0
	#second = int(math.floor(seconds))
	
	#if abs((second+60*minute+3600*hour)-utcent) > 2:
	#	print "Nasty error"
	#	sys.exit()
	
	#t = time.mktime((year, month, day, hour, minute, second, 0, 0, 0))
	#print t
	
	fracday=utcent/86400.0

	j1 = 367*year - int(7*(year+int((month+9)/12))/4)
	j2 = -int((3*((year + int((month-9)/7))/100+1))/4)
	j3 = int(275*month/9) + day + 1721029 - 0.5
	jd = j1 + j2 + j3 + fracday
	
	#print jd
	
	return jd
"""



"""
Old stuff from Christel :

############
# Maidanak #
############

full size = 2030x800 pixels
scale = 0.266" per pixel
field of view = 8.5x3.5 arcmin
readout noise = 5.3 e- 
gain = 1.16 e-/ADU


Time zone = GMT+5 hours to the east
Long = +66.89641 deg
Lat  = +38.67332 deg 
Altitude = 2593 m
Seeing_median = 0.69"

Optical configuration: Ritchy-Chretien 
Two focal mode = a) f/7.74    <=======
                 b) f/17.34
Diameter = 1.5 m

SITe 2000x800 CCD:

full size = 2030x800 pixels
pixel size = 15 mkm 
scale = 0.266" per pixel in f/7.74   <======
        0.119" per pixel in f/17.34
field of view = 8.5x3.5 arcmin in f/7.74   <======
              = 4.0x1.6 arcmin in f/17.34
cooling agent = liquid nitrogen 
readout noise = 5.3 e- 
gain = 1.16 e-/ADU
filter set: Bessell UBVRcIc   RC   <======

"""

