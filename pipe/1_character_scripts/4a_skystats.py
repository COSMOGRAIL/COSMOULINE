"""
    We measure level and stddev of the sky, with custom python.
    This is in electrons !!!
    You can turn on the flag "checkplots" to check how I do this.
"""
import numpy as np
import sys
import os
# if ran as a script, append the parent dir to the path
sys.path.append(os.path.dirname(sys.path[0]))
# if ran interactively, append the parent manually as sys.path[0] 
# will be emtpy.
sys.path.append('..')

from config import alidir, dbbudir, computer, imgdb, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import backupfile, proquest, nicetimediff, notify


from datetime import datetime
from astropy.io import fits

checkplots = settings['checkplots']
askquestions = settings['askquestions']

if checkplots :
    import matplotlib.pyplot as plt

# We select the images :
db = KirbyBase(imgdb)
if settings['thisisatest'] :
    print("This is a test run.")
    images = db.select(imgdb, ['gogogo','treatme', 'testlist'], 
                              [True, True, True], returnType='dict')
elif settings['update']:
    print("This is an update !")
    images = db.select(imgdb, ['gogogo','treatme', 'updating'], 
                              [True, True, True], returnType='dict')
    askquestions = False
else :
    images = db.select(imgdb, ['gogogo','treatme'], 
                              [True, True], returnType='dict')

nbrofimages = len(images)
print("Number of images to treat :", nbrofimages)
proquest(askquestions)

if not checkplots : # Then we will update the database.
    # We make a backup copy of our database :
    backupfile(imgdb, dbbudir, "skystats")

    # We add some new fields into the database : 
    if "skylevel" not in db.getFieldNames(imgdb) :
        db.addFields(imgdb, ['skylevel:float', 'prealistddev:float'])


starttime = datetime.now()

for i,image in enumerate(images):

    print("- " * 40)
    print("%i / %i : %s" % (i+1, nbrofimages, image['imgname']))
    
    # Read the FITS file as numpy array :
    filename = os.path.join(alidir, image['imgname']+".fits")
    pixelarray, header = fits.getdata(filename, header=True)
    
    
    # This is to put it in right orientation, would not be needed here.
    pixelarray = np.asarray(pixelarray).transpose() 
    
    # Print some info about the image :
    pixelarrayshape = pixelarray.shape
    print("(%i, %i), %s, %s" % (pixelarrayshape[0], pixelarrayshape[1], \
                                header["BITPIX"], pixelarray.dtype.name))
    
    # Ready to rock. (Hell yeah!)
    # So we want to get the sky level, 
    # and the std dev of the pixels around this level (noise in sky).
    medianlevel = np.nanmedian(pixelarray.ravel())
    
    # We cut between 0 and twice the medianlevel :
    nearskypixvals = pixelarray[np.logical_and(pixelarray > 0, 
                                               pixelarray < 2*medianlevel)]
    
    
    # First approximation :
    skylevel = np.nanmedian(nearskypixvals.ravel())
    skystddev = np.nanstd(nearskypixvals.ravel())
    
    # we iterate once more, cutting at 4 sigma :
    nearskypixvals = nearskypixvals[np.logical_and(\
                               nearskypixvals > skylevel - 4.0 * skystddev, 
                               nearskypixvals < skylevel + 4.0 * skystddev)]
    
    # Final approximation :
    skylevel = np.nanmedian(nearskypixvals.ravel())
    skystddev = np.nanstd(nearskypixvals.ravel())
    
    print(f"Sky level at {skylevel:f}, noise of {skystddev:f}")
        
    if checkplots :
        plt.hist(pixelarray.ravel(), facecolor='green', 
                 bins=np.linspace(0,3*medianlevel,100), normed=True, log=False)
        #plt.plot(bin_centers, hist, "b.")
        plt.axvline(x=medianlevel, linewidth=2, color='green', label='median')
        plt.axvline(x=skylevel, linewidth=2, color='red', label='skylevel')
        plt.axvline(x=skylevel - 1*skystddev, linewidth=2, color='blue', 
                   label='skylevel - skystddev')
        plt.axvline(x=skylevel + 1*skystddev, linewidth=2, color='blue', 
                   label='skylevel + skystddev')
        plt.xlabel("Pixel value [ADU]")
        plt.title('Histogram of all pixel values for image %s: %s'\
                   %(image['imgname'], image['testcomment']))
        plt.legend(loc='best')
        plt.show()
        print("Remember : the database is NOT UPDATED !")
    else:
        db.update(imgdb, ['recno'], [image['recno']],
                  {'skylevel': float(skylevel), \
                   'prealistddev': float(skystddev)})
    
if not checkplots :
    db.pack(imgdb) # To erase the blank lines
    

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, settings['withsound'], f"I'me done. It took me {timetaken}")
