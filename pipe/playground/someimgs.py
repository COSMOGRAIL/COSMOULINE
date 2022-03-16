exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))

from kirbybase import KirbyBase, KBError
from variousfct import *

db = KirbyBase()

#images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['setname', 'mhjd'])

images = db.select(imgdb, ['recno'], ['*'], returnType='dict', sortFields=['mhjd'])

"""
                 nbrcoeffstars  <type 'int'>
                 maxcoeffstars  <type 'int'>
                      medcoeff  <type 'float'>
                      sigcoeff  <type 'float'>
                     spancoeff  <type 'float'>
                        stddev  <type 'float'>
                   geomapangle  <type 'float'>
                     geomaprms  <type 'float'>
                   geomapscale  <type 'float'>
                       flagali  <type 'int'>
                   nbralistars  <type 'int'>
                   maxalistars  <type 'int'>
                         angle  <type 'float'>
                    alicomment  <type 'str'>
                        seeing  <type 'float'>
                           ell  <type 'float'>
                     goodstars  <type 'int'>
                  seeingpixels  <type 'float'>
                      skylevel  <type 'float'>
                  prealistddev  <type 'float'>
                           hjd  <type 'str'>
                          mhjd  <type 'float'>
                      calctime  <type 'str'>
                           alt  <type 'float'>
                            az  <type 'float'>
                       airmass  <type 'float'>
                   moonpercent  <type 'float'>
                      moondist  <type 'float'>
                       moonalt  <type 'float'>
                       sundist  <type 'float'>
                        sunalt  <type 'float'>
                    astrofishy  <type 'bool'>
                  astrocomment  <type 'str'>
                       imgname  <type 'str'>
                       treatme  <type 'bool'>
                        gogogo  <type 'bool'>
                        whynot  <type 'str'>
                 telescopename  <type 'str'>
                       setname  <type 'str'>
                        rawimg  <type 'str'>
                 scalingfactor  <type 'float'>
                       pixsize  <type 'float'>
                          date  <type 'str'>
                         datet  <type 'str'>
                            jd  <type 'str'>
                           mjd  <type 'float'>
            telescopelongitude  <type 'str'>
             telescopelatitude  <type 'str'>
            telescopeelevation  <type 'float'>
                       exptime  <type 'float'>
                          gain  <type 'float'>
                   origin_gain  <type 'float'>
                     readnoise  <type 'float'>
                       rotator  <type 'float'>
                   satur_level  <type 'float'>
                preredcomment1  <type 'str'>
                preredcomment2  <type 'str'>
                  preredfloat1  <type 'float'>
                  preredfloat2  <type 'float'>
		  
"""

selimages = [image for image in images if image["telescopename"] == "EulerC2" and image["date"][0:4] == "2008" and image["gogogo"] == True]

for image in selimages:
	#print "%s %s" % (image["imgname"], image["date"])
	#print  "cp %s /home/epfl/tewes/unsaved/pack/." % (image["rawimg"])

	print("%s.fits\t%.7f\t%s" % (image["imgname"][2:], image["mhjd"], image["datet"]))


#print len(selimages)
