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

print("Re-exec config :")
exec(compile(open("../config.py", "rb").read(), "../config.py",
             'exec'))  # yes, this line is required so that settings.py are available within the functions below.


def juliandate(pythondt):
    """
    Returns the julian date from a python datetime object
    """

    # year = int(year)
    # month = int(month)
    # day = int(day)

    year = int(pythondt.strftime("%Y"))
    month = int(pythondt.strftime("%m"))
    day = int(pythondt.strftime("%d"))

    hours = int(pythondt.strftime("%H"))
    minutes = int(pythondt.strftime("%M"))
    seconds = int(pythondt.strftime("%S"))

    fracday = float(hours + float(minutes) / 60.0 + float(seconds) / 3600.0) / 24.0
    # fracday = 0

    # First method, from the python date module. It was wrong, I had to subtract 0.5 ...
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jd1 = day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    jd1 = jd1 + fracday - 0.5

    # Second method (I think I got this one from Fundamentals of Astronomy)
    # Here the funny -0.5 was part of the game.

    j1 = 367 * year - int(7 * (year + int((month + 9) / 12)) / 4)
    j2 = -int((3 * ((year + int((month - 9) / 7)) / 100 + 1)) / 4)
    j3 = int(275 * month / 9) + day + 1721029 - 0.5
    jd2 = j1 + j2 + j3 + fracday

    # print "Date: %s" % pythondt.strftime("%Y %m %d  %H:%M:%S")
    # print "jd1 : %f" % jd1
    # print "jd2 : %f" % jd2

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

    dayofwk = int(math.fmod(int(JD + 1.5), 7))
    (F, Z) = math.modf(JD + 0.5)
    Z = int(Z)

    if JD < 2299160.5:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)

    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)

    day = B - D - int(30.6001 * E) + F
    nday = B - D - 123
    if nday <= 305:
        dayofyr = nday + 60
    else:
        dayofyr = nday - 305
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
    (dfrac, days) = math.modf(day / 1.0)
    (hfrac, hours) = math.modf(dfrac * 24.0)
    (mfrac, minutes) = math.modf(hfrac * 60.0)
    seconds = round(mfrac * 60.0)  # seconds are rounded

    if seconds > 59:
        seconds = 0
        minutes = minutes + 1
    if minutes > 59:
        minutes = 0
        hours = hours + 1
    if hours > 23:
        hours = 0
        days = days + 1

    return datetime.datetime(year, month, int(days), int(hours), int(minutes), int(seconds))


###############################################################################################

# And now the functions that know how to read the headers

###############################################################################################

def eulerc2header(rawimg):
    print (rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    pixsize = 0.344
    readnoise = 9.5  # Taken from Christel
    scalingfactor = 0.5612966  # measured scalingfactor (with respect to Mercator = 1.0)
    saturlevel = 65000.0  # arbitrary

    telescopelongitude = "-70:43:48.00"
    telescopelatitude = "-29:15:24.00"
    telescopeelevation = 2347.0

    header = pyfits.getheader(rawimg)

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    if "DATE-OBS" in header:  # This should be the default way of doing it.
        pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19],
                                              "%Y-%m-%dT%H:%M:%S")  # This is the start of the exposure.
    else:
        if "TUNIX_DP" in header:  # For the very first images
            pythondt = datetime.datetime.utcfromtimestamp(float(header["TUNIX_DP"]))
            print ("I have to use TUNIX_DP :", pythondt)

    if "EXPTIME" in header:  # Nearly always available.
        exptime = float(header['EXPTIME'])  # in seconds.
    elif "TIMEFF" in header:
        exptime = float(header['TIMEFF'])
        print ("I have to use TIMEFF :", exptime)
    else:
        print ("WTF ! No exptime !")
        exptime = 360.0

    pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

    # Now we produce the date and datet fields, middle of exposure :

    date = pythondt.strftime("%Y-%m-%d")
    datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

    myownjdfloat = juliandate(pythondt)  # The function from headerstuff.py
    myownmjdfloat = myownjdfloat - 2400000.5

    # We perform some checks with other JD-like header keywords if available :
    if "MJD-OBS" in header:
        headermjdfloat = float(header['MJD-OBS'])  # should be the middle of exposure, according to hdr comment.
        if abs(headermjdfloat - myownmjdfloat) > 0.0001:
            raise mterror("MJD-OBS disagrees !")

    jd = "%.6f" % myownjdfloat
    mjd = myownmjdfloat

    rotator = 0.0

    # The gain, we need to read 3 headers.
    # The options are written in order of "trust", the most trusted first.
    gain = 0.0
    if "CCD_SGAI" in header:  # old images
        gain = float(header['CCD_SGAI'])
        print ("Reading gain from CCD_SGAI")
    elif "OGE DET SGAI" in header:  # intermediary, just after the header format change
        gain = float(header['HIERARCH OGE DET SGAI'])
        print ("Reading gain from OGE DET SGAI")
    elif "ESO CAM CCD SGAI" in header:  # The current format
        gain = float(header['HIERARCH ESO CAM CCD SGAI'])
        print ("Reading gain from ESO CAM CCD SGAI")
    elif "ESO CAM2 CCD GAIN" in header:  # was also used once in the transition phase 04/2009
        gain = float(header["HIERARCH ESO CAM2 CCD GAIN"])
        print ("Reading gain from ESO CAM2 CCD GAIN")
    elif "ESO CAM CCD GAIN" in header:  # was also used once in the transition phase 04/2009
        gain = float(header["HIERARCH ESO CAM CCD GAIN"])
        print ("Reading gain from ESO CAM CCD GAIN")
    elif "CCD_FGAI" in header:  # Very very old ones ... Be careful, this was in ADU/e
        gain = 1.0 / float(header["CCD_FGAI"])

    # We do a quick check :
    if gain < 0.5 or gain > 3.0:
        print (header)
        raise mterror("gain = %f ???" % gain)

    # The pre-reduction info :
    # preredcomment1 = "None"
    # preredcomment2 = "None"
    # preredfloat1 = 0.0
    # preredfloat2 = 0.0
    preredcomment1 = str(header["PR_NFLAT"])
    preredcomment2 = str(header["PR_NIGHT"])
    preredfloat1 = float(header["PR_FSPAN"])
    preredfloat2 = float(header["PR_FDISP"])

    # We return a dictionnary containing all this info, that is ready to be inserted into the database.
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


###############################################################################################

def eulercamheader(rawimg):
    print(rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    pixsize = 0.2148  # Measured on an image, Malte
    gain = 2.7  # Rough mean of Monika's measure in Q1, might get updated.
    readnoise = 5.0  # typical value for quadrant 1, i.e. also all LL frames.
    scalingfactor = 0.89767829371  # measured scalingfactor (with respect to Mercator = 1.0)
    saturlevel = 65000.0  # arbitrary
    rotator = 0.0

    telescopelongitude = "-70:43:48.00"
    telescopelatitude = "-29:15:24.00"
    telescopeelevation = 2347.0

    header = pyfits.getheader(rawimg)
    # availablekeywords = header.ascardlist().keys() # depreciated, not needed anyway

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

    # The pre-reduction info :
    # preredcomment1 = "None"
    # preredcomment2 = "None"
    # preredfloat1 = 0.0
    # preredfloat2 = 0.0
    preredcomment1 = str(header["PR_NFLAT"])
    preredcomment2 = str(header["PR_FORMA"])  # There was the "NIGHT" before, but the format is more important.
    if "PR_FSPAN" in list(header.keys()):
        preredfloat1 = float(header["PR_FSPAN"])
    else:
        preredfloat1 = None
    if "PR_FDISP" in list(header.keys()):
        preredfloat2 = float(header["PR_FDISP"])
    else:
        preredfloat2 = None

    # We return a dictionnary containing all this info, that is ready to be inserted into the database.
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


###############################################################################################


def mercatorheader(rawimg):
    print(rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    pixsize = 0.19340976
    gain = 0.93  # e- / ADU, as given by Saskia Prins
    readnoise = 9.5  # ?
    scalingfactor = 1.0  # By definition, others are relative to Mercator.
    saturlevel = 65000.0  # arbitrary

    telescopelongitude = "-17:52:47.99"
    telescopelatitude = "28:45:29.99"
    telescopeelevation = 2327.0

    header = pyfits.getheader(rawimg)
    availablekeywords = list(header.keys())

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    if len(header["DATE-OBS"]) >= 19:
        pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19], "%Y-%m-%dT%H:%M:%S")

    if len(header["DATE-OBS"]) == 10:
        pythondt = datetime.datetime.utcfromtimestamp(float(header["TUNIX_DP"]))
        print("Warning : I had to use TUNIX_DP : %s" % pythondt)
        print("(But this should be ok)")

    exptime = float(header['EXPTIME'])  # in seconds.

    pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

    # Now we produce the date and datet fields, middle of exposure :

    date = pythondt.strftime("%Y-%m-%d")
    datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

    myownjdfloat = juliandate(pythondt)  # The function from headerstuff.py
    myownmjdfloat = myownjdfloat - 2400000.5

    # We perform some checks with other JD-like header keywords if available :
    if "MJD" in availablekeywords:
        headermjdfloat = float(header['MJD'])  # should be the middle of exposure, according to hdr comment.
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
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


###############################################################################################


def liverpoolheader(rawimg):
    """
    Reading the header of 2010 RATCam LRT images.
    Probably also ok for previous RATCam images.
    """
    print(rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    # pixsize = 0.279 # (if a 2 x 2 binning is used)
    pixsize = 0.135  # (if a 1 x 1 binning is used, as we do for cosmograil)
    # hmm in the header they give 0.1395 ???

    # gain = 0 # We will take it from the header, it's around 2.2, keyword GAIN
    # readnoise = 0.0 # idem, keyword READNOIS, 7.0
    scalingfactor = 1.0  # Not measured : to be done !
    saturlevel = 65000.0  # arbitrary

    telescopelongitude = "-17:52:47.99"  # Same location as Mercator ...
    telescopelatitude = "28:45:29.99"
    telescopeelevation = 2327.0

    header = pyfits.getheader(rawimg)
    availablekeywords = list(header.keys())

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
    pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19], "%Y-%m-%dT%H:%M:%S")  # beginning of exposure in UTC
    exptime = float(header['EXPTIME'])
    pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

    # Now we produce the date and datet fields, middle of exposure :
    date = pythondt.strftime("%Y-%m-%d")
    datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

    myownjdfloat = juliandate(pythondt)
    myownmjdfloat = myownjdfloat - 2400000.5
    jd = "%.6f" % myownjdfloat
    mjd = myownmjdfloat

    # Quick test agains header mjd :
    headermjd = float(header['MJD'])
    if abs(myownmjdfloat - headermjd) > 0.01:  # loose, as we have added exptime/2 ...
        raise mterror("Header DATE-OBS and MJD disagree !!!")

    # The pre-reduction info :
    preredcomment1 = "None"
    preredcomment2 = "None"
    preredfloat1 = 0.0
    preredfloat2 = 0.0

    # We return a dictionnary containing all this info, that is ready to be inserted into the database.
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


###############################################################################################


def maidanaksiteheader(rawimg):
    """
    Maidanak SITE = raw image format 2030 x 800
    Written 2010 Malte & Denis
    For image prereduced by pypr in 2010
    """
    print(rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    pixsize = 0.266
    gain = 1.16  # From Ildar, to be checked ?
    readnoise = 5.3  # idem
    scalingfactor = 0.723333  #
    saturlevel = 65000.0  # arbitrary

    telescopelongitude = "66:53:47.07"
    telescopelatitude = "38:40:23.95"
    telescopeelevation = 2593.0

    header = pyfits.getheader(rawimg)
    availablekeywords = list(header.keys())

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    rotator = 0.0

    # Now the date and time stuff :

    if not (len(header["DATE-OBS"]) == 10 and len(header["DATE"]) == 10):
        print("Length error in DATE-OBS and DATE!")
        # raise mterror("Length error in DATE-OBS and DATE")
    if header["DATE-OBS"] != header["DATE"]:
        print("DATE-OBS : %s" % (header["DATE-OBS"]))
        print("DATE : %s" % (header["DATE"]))
        print("TM_START : %s" % (header["TM_START"]))
        # raise mterror("DATE-OBS and DATE do not agree")

    pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:10], "%Y-%m-%d")
    pythondt += datetime.timedelta(seconds=header["TM_START"])
    exptime = float(header['EXPTIME'])
    if (exptime < 10.0) or (exptime > 1800):
        print("Exptime : ", exptime)
        # raise mterror("Problem with exptime...")

    pythondt += datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

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
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


###############################################################################################


def maidanaksiheader(rawimg):
    """
    Maidanak SI = raw image format 4096 x 4096
    Written 2010 Malte & Gianni
    For image prereduced by pypr in 2010
    """
    print(rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    pixsize = 0.266
    gain = 1.45
    readnoise = 4.7
    scalingfactor = 0.721853  # measured scalingfactor (with respect to Mercator = 1.0)#
    saturlevel = 65000.0  # arbitrary

    telescopelongitude = "66:53:47.07"
    telescopelatitude = "38:40:23.95"
    telescopeelevation = 2593.0

    header = pyfits.getheader(rawimg)
    # availablekeywords = header.keys()

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    rotator = 0.0

    # Now the date and time stuff :

    dateobsstring = "%sT%s" % (header["UTDATE"][0:10], header["UTSTART"])  # looks like standart DATE-OBS field
    pythondt = datetime.datetime.strptime(dateobsstring, "%Y-%m-%dT%H:%M:%S")  # beginning of exposure in UTC
    exptime = float(header['EXPTIME'])
    pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

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
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
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
    print(rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    pixsize = 0.4262
    gain = 1.5
    readnoise = 10.0
    scalingfactor = 0.450486  # (with respect to Mercator = 1.0)
    saturlevel = 65000.0  # arbitrary

    telescopelongitude = "66:53:47.07"
    telescopelatitude = "38:40:23.95"
    telescopeelevation = 2593.0

    header = pyfits.getheader(rawimg)
    # availablekeywords = header.keys()

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    rotator = 0.0

    # Now the date and time stuff :

    pythondt = datetime.datetime.strptime(header["DATE-OBS"][0:19], "%Y-%m-%dT%H:%M:%S")  # beginning of exposure in UTC
    exptime = float(header['EXPTIME'])
    pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

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
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


###############################################################################################
def Maidanak_2_5kheader(rawimg):
    print(rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    header = pyfits.getheader(rawimg)

    pixsize = 0.268  # from Otabek and IDlar in 2018
    gain = 1.45  #
    readnoise = 4.7  #
    scalingfactor = 1.0  # measured scalingfactor (with respect to Mercator = 1.0)
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
    print(rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    pixsize = 0.296
    gain = 0.28  # 1.22 old camera
    readnoise = 5.75  # 4.8
    scalingfactor = 0.65189  # measured scalingfactor (with respect to Mercator = 1.0)#
    saturlevel = 65000.0  # arbitrary

    telescopelongitude = "78:57:50.99"
    telescopelatitude = "32:46:46.00"
    telescopeelevation = 4500.0

    header = pyfits.getheader(rawimg)
    availablekeywords = list(header.keys())

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

    pythondt += datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

    # Now we produce the date and datet fields, middle of exposure :
    date = pythondt.strftime("%Y-%m-%d")
    datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

    myownjdfloat = juliandate(pythondt)
    myownmjdfloat = myownjdfloat - 2400000.5
    jd = "%.6f" % myownjdfloat
    mjd = myownmjdfloat

    # The pre-reduction info :
    # preredcomment1 = str(header["PR_NFLAT"])
    # preredcomment2 = str(header["PR_NIGHT"])
    # preredfloat1 = float(header["PR_FSPAN"])
    # preredfloat2 = float(header["PR_FDISP"])

    preredcomment1 = "na"
    preredcomment2 = "na"
    preredfloat1 = 0.0
    preredfloat2 = 0.0

    # We return a dictionnary containing all this info, that is ready to be inserted into the database.
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


###############################################################################################

def holiheader(rawimg):  # HoLiCam header
    """
    HoliCam header, adapted together with Dominik Klaes
    """

    print(rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    pixsize = 0.21  # Holicam, taken from http://www.astro.uni-bonn.de/~ccd/holicam/holicam.htm
    gain = 2.5  # idem
    readnoise = 9.0  # idem
    scalingfactor = 1.0  # not yet measured ! Do so if required !
    saturlevel = 65000.0  # arbitrary

    telescopelongitude = "6:51:00.00"
    telescopelatitude = "50:09:48.00"
    telescopeelevation = 549.0
    # Images are in natural orientation

    header = pyfits.getheader(rawimg)
    # date = str(header['DATE-OBS']) # this does not work for Holicam, funny problem.
    # But there is an alternative : (doesn't work anymore in 2017)
    # headerascardlist = header.cards()
    # headerascardlist["DATE-OBS"].verify("fix")

    # Here is the proper fix :
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

    pythondt += datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

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
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
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
    print(rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

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
        availablekeywords = list(header.keys())
    except:
        availablekeywords = [card[0] for card in header.cards]

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    # CAREFUL with these: we fill the header with NA to go on with the deconv...

    if "CCDFLTID" not in availablekeywords:
        print("WARNING !!! No CCDFILTID in the headers !!")
        # proquest(askquestions)
        print("You can disable me in /pipe/module/headerstuff line 901")

    if "CCDFLTID" in availablekeywords:
        # Quick check of filter :
        if header["CCDFLTID"].strip() != "R":
            print("\n\n\n WARNING : Filter is not R\n\n\n")

    if "JD" in availablekeywords:
        headerjd = float(header['JD'])  # Should be UTC, beginning of exposure
    else:
        print("WARNING !!! No JD in the headers. Going for HJD instead !!")
        # proquest(askquestions)
        headerjd = float(header['HJD'])
        print("You can disable me in /pipe/module/headerstuff line 913")

    if "EXPTIME" in availablekeywords:
        exptime = float(header['EXPTIME'])  # in seconds
    else:
        print("WARNING !!! No EXPTIME in the headers. Adding 300[s] as default !!")
        # proquest(askquestions)
        exptime = float(300.0)  # in seconds
        print("You can disable me in /pipe/module/headerstuff line 921")

    pythondt = DateFromJulianDay(headerjd)
    pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

    # Now we produce the date and datet fields, middle of exposure :

    date = pythondt.strftime("%Y-%m-%d")
    datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

    myownjdfloat = juliandate(pythondt)  # The function from headerstuff.py
    myownmjdfloat = myownjdfloat - 2400000.5  # modified Julian days
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
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


###############################################################################################


def skysimheader(rawimg):
    """
    skysim = skymaker simulated images
    Written 2010 Gianni
    """

    print(rawimg)
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    header = pyfits.getheader(rawimg)
    availablekeywords = header.keys()

    pixsize = float(header['PIXSIZE'])
    gain = float(header['GAIN'])
    readnoise = float(header['RON'])
    scalingfactor = 1.0
    saturlevel = 65000.0  # arbitrary

    telescopelongitude = "00:00:00.00"
    telescopelatitude = "00:00:00.00"
    telescopeelevation = 0.0

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    rotator = 0.0

    dateobsstring = "%s" % (header["DATE-OBS"])  # looks like standart DATE-OBS field
    pythondt = datetime.datetime.strptime(dateobsstring, "%Y-%m-%dT%H%M%S")  # beginning of exposure in UTC
    exptime = float(header['EXPOTIME'])
    pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

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
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


def VSTheader(rawimg):
    """
    Version for VST images
    Experimental
    """
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    header = pyfits.getheader(rawimg)
    pixsize = 0.215
    gain = header['GAIN']
    if gain == 0.0:
        gain = 1.9
    print("image : %s, gain : %2.4f" % (imgname, gain))
    readnoise = 2.1  # from the Health check report in May 2019
    scalingfactor = 1.0  # no need for it right now...
    saturlevel = header['SATLEVEL']  # in ADU
    rotator = 0.0  # useless

    telescopelongitude = "-70:24:10.19"
    telescopelatitude = "-24:37:22.79"  # paranal
    telescopeelevation = 2635.0

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    pythondt = datetime.datetime.strptime(header["OBSTART"], "%Y-%m-%dT%H:%M:%S")  # This is the start of the exposure.
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
    # May be useful one day...can be used.
    preredcomment1 = "Zero Point"
    preredcomment2 = "None"
    preredfloat1 = header['ZP']
    preredfloat2 = 0.0

    # We return a dictionnary containing all this info, that is ready to be inserted into the database.
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


###############################################################################################

def Stancamheader(rawimg):
    """
    Version for NOT stancam images
    """
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    header = pyfits.getheader(rawimg)
    pixsize = 0.176
    gain = 1.68  # from http://www.not.iac.es/instruments/stancam/stancamover.html
    print ("image : %s, gain : %2.4f" % (imgname, gain))
    readnoise = 6.5
    scalingfactor = 1.0  # no need for it right now...
    saturlevel = 65536.0  # in ADU
    rotator = 0.0  # useless

    telescopelongitude = "-17:53:06.00"
    telescopelatitude = "28:24:10.00"
    telescopeelevation = 2382.0

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    pythondt = datetime.datetime.strptime(header["DATE-AVG"][:-2],
                                          "%Y-%m-%dT%H:%M:%S")  # This is the middle of the exposure
    exptime = float(header['EXPTIME'])  # in seconds.

    # pythondt = pythondt + datetime.timedelta(seconds = exptime/2.0) # This is the middle of the exposure.

    # Now we produce the date and datet fields, middle of exposure :

    date = pythondt.strftime("%Y-%m-%d")
    datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

    myownjdfloat = juliandate(pythondt)  # The function from headerstuff.py
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
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


def VST_mosaic_header(rawimg):
    """
    Version for VST mosaic images
    Experimental
    """
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    header = pyfits.getheader(rawimg)
    pixsize = 0.215
    gain = header['GAIN']
    print("image : %s, gain : %2.4f" % (imgname, gain))
    readnoise = 2.1  # from the Health check report in May 2019
    scalingfactor = 1.0  # no need for it right now...
    saturlevel = header['SATLEVEL']  # in ADU
    rotator = 0.0  # useless

    telescopelongitude = "-70:24:10.19"
    telescopelatitude = "-24:37:22.79"  # paranal
    telescopeelevation = 2635.0

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    pythondt = datetime.datetime.strptime(header["DATE"], "%Y-%m-%dT%H:%M:%S")  # This is the start of the exposure.
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
    # May be useful one day...can be used.
    preredcomment1 = "None"
    preredcomment2 = "None"
    preredfloat1 = 0.0
    preredfloat2 = 0.0

    # We return a dictionnary containing all this info, that is ready to be inserted into the database.
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


def VATTheader(rawimg):
    """
    Version for VATT images
    Written by Martin, 09.2019
    """
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    header = pyfits.getheader(rawimg)
    pixsize = 0.187
    gain = 1.730
    print("image : %s, gain : %2.4f" % (imgname, gain))
    readnoise = 5.1  # from the http://www.public.asu.edu/~rjansen/vatt/vatt4k.html
    scalingfactor = 1.0  # no need for it right now...
    saturlevel = 65535.0  # in ADU
    rotator = 0.0  # useless

    telescopelongitude = "-109:53:31.00"
    telescopelatitude = "32:42:05.00"  # MT Graham, AZ
    telescopeelevation = 3178.0

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    pythondt = datetime.datetime.strptime(header["DATE-OBS"] + "T" + header["TIME-OBS"][:-4],
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
    # May be useful one day...can be used.
    preredcomment1 = "None"
    preredcomment2 = "None"
    preredfloat1 = 0.0
    preredfloat2 = 0.0

    # We return a dictionnary containing all this info, that is ready to be inserted into the database.
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict


def LCOheader(rawimg):
    """
    Version for LCO images
    Experimental
    """
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension
    hdu = fits.open(rawimg)
    header = hdu[0].header
    pixsize = header['PIXSCALE']
    gain = header['GAIN']
    print("image : %s, gain : %2.4f" % (imgname, gain))
    readnoise = header['RDNOISE']  # from the Health check report in May 2019
    scalingfactor = 1.0  # no need for it right now...
    saturlevel = header['SATURATE']  # in ADU
    rotator = 0.0  # useless

    telescopelongitude = "-156:15:21.6"
    telescopelatitude = "20:42:27.0"  # haleakala
    telescopeelevation = 3055.0

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    pythondt = datetime.datetime.strptime(header["DATE-OBS"][:-4],
                                          "%Y-%m-%dT%H:%M:%S")  # This is the start of the exposure.
    exptime = float(header['EXPTIME'])  # in seconds.
    Filter  = header['filter']
    
    pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

    # Now we produce the date and datet fields, middle of exposure :

    date = pythondt.strftime("%Y-%m-%d")
    datet = pythondt.strftime("%Y-%m-%dT%H:%M:%S")

    myownjdfloat = juliandate(pythondt)  # The function from headerstuff.py
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
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2,
                  'filter': Filter
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


###############################################################################################


def noheader(rawimg):
    imgname = setname + "_" + os.path.splitext(os.path.basename(rawimg))[0]  # drop extension

    pixsize = 1.0
    gain = 1.0
    readnoise = 5.0
    scalingfactor = 1.0
    saturlevel = 65000.0  # arbitrary

    telescopelongitude = "00:00:00.00"
    telescopelatitude = "00:00:00.00"
    telescopeelevation = 0.0

    treatme = True
    gogogo = True
    whynot = "na"
    testlist = False
    testcomment = "na"

    pythondt = datetime.datetime.strptime("2002-10-10T13:37:00", "%Y-%m-%dT%H:%M:%S")  # 2000-00-00 was not working...
    exptime = 300.0
    pythondt = pythondt + datetime.timedelta(seconds=exptime / 2.0)  # This is the middle of the exposure.

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
    returndict = {'imgname': imgname, 'treatme': treatme, 'gogogo': gogogo, 'whynot': whynot, 'testlist': testlist,
                  'testcomment': testcomment,
                  'telescopename': telescopename, 'setname': setname, 'rawimg': rawimg,
                  'scalingfactor': scalingfactor, 'pixsize': pixsize, 'date': date, 'datet': datet, 'jd': jd,
                  'mjd': mjd,
                  'telescopelongitude': telescopelongitude, 'telescopelatitude': telescopelatitude,
                  'telescopeelevation': telescopeelevation,
                  'exptime': exptime, 'gain': gain, 'readnoise': readnoise, 'rotator': rotator,
                  'saturlevel': saturlevel,
                  'preredcomment1': preredcomment1, 'preredcomment2': preredcomment2, 'preredfloat1': preredfloat1,
                  'preredfloat2': preredfloat2
                  }

    return returndict

def PANSTARRSheader(rawimg):
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

def UH2m2header(rawimg):
	print (rawimg)
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