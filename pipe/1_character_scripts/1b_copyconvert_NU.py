#
#  This script will copy the actual images, 
#  and convert them from ADU to electrons
#  You should use it right after the import of the images into the database.
#  Also we completely empty the header

#  We do not update the database


import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import imgdb, settings, alidir

from modules.kirbybase import KirbyBase
from modules.variousfct import proquest, fromfits, tofits


redofromscratch = False
askquestions = settings["askquestions"]
trimheight = settings['trimheight']

db = KirbyBase(imgdb)

if settings['thisisatest']:
    print("This is a test run!")
    images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], 
                              [True, True, True], returnType='dict')
elif settings['update']:
    print("This is an update.")
    images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], 
                              [True, True, True], returnType='dict')
    askquestions = False
else:
    images = db.select(imgdb, ['gogogo', 'treatme'], 
                              [True, True], returnType='dict')

nbrofimages = len(images)

print("I will copy/convert %i images." % (nbrofimages))
proquest(askquestions)



for i, image in enumerate(images):
    
    # check if file exists
    print(image['imgname'])
    outfilename = os.path.join(alidir, image['imgname'] + ".fits")
    print(i+1, "/", nbrofimages, " : ", 
          image['imgname'], f", gain = {image['gain']:.3f}")
    
    if not redofromscratch:
        if os.path.isfile(outfilename):
            print("Image already exists. I skip...")
            #pass
            continue
        

    pixelarray, header = fromfits(image['rawimg'])
    if trimheight >= 1:
        trimheight = int(trimheight) # just to make sure ...
        pixelarray = pixelarray[:, trimheight:-trimheight]
    
    pixelarray = pixelarray * image['gain']
    # so that we have an image in electrons and not in ADU
        
    tofits(outfilename, pixelarray)
    # we clean the header to avoid dangerous behaviors from iraf or sextractor


print("Done with copy/conversion.")


