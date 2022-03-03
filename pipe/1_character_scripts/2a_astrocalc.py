#
#    Performs some "astronomical" calculations (most important : hjd), 
#   using pyephem.
#    Adds a lot of not-that-important entries to the database :-)
#

import ephem 
import math
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import imgdb, dbbudir, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import proquest, backupfile

askquestions = settings['askquestions']
xephemlens = settings['xephemlens']

def airmass(radalt):
    # We calculate the airmass (radalt is altitude in radians)
    # Rozenberg's empirical relation :
    # X = 1 / [sin ho + 0.025 exp(-11 sin ho)]
    # where ho is the apparent altitude of the object. 
    # This formula can be used all down to the horizon (where it gives X = 40).

    if radalt < 0.0:
        return -1.0
    elif radalt > math.pi/2.0:
        return -2.0
    else :
        return 1.0 / (math.sin(radalt) + .025*math.exp(-11.0*math.sin(radalt)))


db = KirbyBase(imgdb)

if settings['update']:
    images = db.select(imgdb, ['gogogo','treatme', 'updating'], 
                              [True, True, True], 
                              returnType='dict')
    askquestions = False
else:
    images = db.select(imgdb, ['gogogo','treatme'], 
                              [True, True], 
                              returnType='dict')

nbrofimages = len(images)
print("Number of images to treat :", nbrofimages)
proquest(askquestions)


print("Doublecheck that this is true : ", xephemlens)
proquest(askquestions)

# We make a backup copy of our database.
backupfile(imgdb, dbbudir, "astrocalc")

# We add some new fields into the holy database.
if "hjd" not in db.getFieldNames(imgdb) :
    db.addFields(imgdb, ['hjd:str', 'mhjd:float', 'calctime:str', "alt:float", \
                         'az:float', 'airmass:float', 'moonpercent:float', \
                         'moondist:float', 'moonalt:float', 'sundist:float', \
                         'sunalt:float', 'astrofishy:bool', 'astrocomment:str'])

for i,image in enumerate(images):

    print("- " * 30)
    print(i+1, "/", nbrofimages, ":", image['imgname'])
    
    # this is a flag we set if we find something fishy...
    # like observation in daylight etc...
    astrofishy = False 
    
    astrocomment = ""
    
    telescope = ephem.Observer()
    telescope.long = image['telescopelongitude']
    telescope.lat = image['telescopelatitude']
    telescope.elevation = image['telescopeelevation']
    telescope.epoch = ephem.J2000

    # DJD = JD - 2415020 is the Dublin Julian Date used by pyephem.
    djd = float(image['jd']) - 2415020.0 # jd is a string !
    telescope.date = djd
    calctime = str(telescope.date)
    print(f"UTC datetime : {calctime}")

    lens = ephem.readdb(xephemlens)
    lens.compute(telescope)
    airmassvalue = airmass(float(lens.alt))
    if (airmassvalue < 1.0) or (airmassvalue > 5.0):
        astrofishy = True
        astrocomment += f"Altitude : {lens.alt} (airmass {airmassvalue:5.2f})."    
    print(f"Altitude : {lens.alt} (airmass {airmassvalue:5.2f}).")
    
    lensalt = float(lens.alt) * 180.00 / math.pi
    lensaz = float(lens.az) * 180.00 / math.pi

    moon = ephem.Moon()
    moon.compute(telescope)

    moonsep = ephem.separation(moon, lens)
    moondist = math.degrees(float(moonsep))
    print(f"Separation to the Moon is {moondist:.2f} degrees.")
    moonpercent = float(moon.phase)
    print(f"Moon illumation : {moonpercent:5.2f} %")
    moonalt=math.degrees(float(moon.alt))
    print(f'Moon altitude [degrees]: {moonalt:.2f}')

    sun = ephem.Sun()
    sun.compute(telescope)
    
    sunalt = math.degrees(float(sun.alt))
    if sunalt > 0.0 :
        astrofishy = True
        astrocomment = astrocomment + f"Sun altitude : {sunalt:.2f} "
    print(f"Sun altitude : {sunalt:.2f}")
    print(f"Sun position : RA {sun.ra} / Dec {sun.dec}")
    # http://en.wikipedia.org/wiki/Heliocentric_Julian_Day
    # If the Sun's celestial coordinates are (ra0,dec0) 
    # and the coordinates of the observed object or event are (ra,dec),
    # and if the distance between the Sun and Earth is d, then
    # HJD = JD - (d/c) [sin(dec) sin(dec0) + cos(dec) cos(dec0) cos(ra-ra0)]

    # the factor d/c, expressed in days:
    dc = (sun.earth_distance * ephem.meters_per_au / ephem.c)/(60.0*60.0*24.0)
    
    rasun = float(sun.ra)
    decsun = float(sun.dec)
    ralens = float(lens.ra)
    declens = float(lens.dec)
    sundist = math.degrees(float(ephem.separation(sun, lens)))

    print(f"Separation to the Sun is {sundist:.2f} degrees.")

    hjd = float(image['jd']) - dc * (math.sin(declens)*math.sin(decsun) \
                   + math.cos(declens)*math.cos(decsun)*math.cos(ralens-rasun))
    # So we calculate hjd based on the julian date 
    # that we got somehow from the header.
    
    mhjd = hjd - 2400000.5
    hjd = f"{hjd:.6f}"

    # some sanity checks, while we are at it
    # should be less than 8.5 minutes:
    if math.fabs(float(image['jd']) - float(hjd)) > 0.0059: 
        astrofishy = True
        nd = math.fabs(image['mjd'] - mhjd)
        astrocomment += f"Sun seems to be a bit far from Earth... {nd:f} days"
    
    # check the date from jd with the date from the FITS header
    # field already in database : date = 2006-03-07
    # output of ephem : 2008/12/20 15:31:58
    
    transfcalctimelist = calctime.split()[0].split("/")
    transfcalctime = "-".join(transfcalctimelist)
    transfdatelist = image['date'].split()[0].split("-")
    
    if (int(transfcalctimelist[0]) != int(transfdatelist[0])) \
        or (int(transfcalctimelist[1]) != int(transfdatelist[1])) \
            or (int(transfcalctimelist[2]) != int(transfdatelist[2])):
        astrofishy = True
        astrocomment += f"FITS date is {image['date']}, calctime is {calctime}?"
        
    # We update the data
    db.update(imgdb, ['recno'], [image['recno']], \
              {'hjd': hjd, 'mhjd':mhjd, 'calctime':calctime, 'alt':lensalt,\
               'az':lensaz, 'airmass':airmassvalue, 'moonpercent':moonpercent,\
               'moondist':moondist, 'moonalt':moonalt, 'sundist':sundist,\
               'sunalt':sunalt, 'astrofishy':astrofishy,\
               'astrocomment':astrocomment})
    
    
db.pack(imgdb) # to erase the blank lines


print("Ok, done.")
print("By the way, did you know that {lens.name}",
      "is located in the constellation {ephem.constellation(lens)[1]}?")




