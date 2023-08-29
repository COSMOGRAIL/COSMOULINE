#
#  This script will copy the actual images, 
#  and convert them from ADU to electrons
#  You should use it right after the import of the images into the database.
#  Also we completely empty the header

#  We do not update the database


import sys
import os
# if ran as a script, append the parent dir to the path
sys.path.append(os.path.dirname(sys.path[0]))
# if ran interactively, append the parent manually as sys.path[0] 
# will be emtpy.
sys.path.append('..')

from config import imgdb, settings, alidir

from modules.kirbybase import KirbyBase
from modules.variousfct import proquest, fromfits, tofits


redofromscratch = False
askquestions = settings["askquestions"]

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

trim_vertical = settings['trim_vertical']
trim_horizontal = settings['trim_horizontal']


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
    
    if trim_vertical > 0:
        pixelarray = pixelarray[:, trim_vertical:-trim_vertical]
    if trim_horizontal > 0:
        pixelarray = pixelarray[trim_horizontal:-trim_horizontal, :]
    
    pixelarray = pixelarray * image['gain']
    # so that we have an image in electrons and not in ADU
        
    tofits(outfilename, pixelarray)
    # we clean the header to avoid dangerous behaviors from iraf or sextractor


print("Done with copy/conversion.")


