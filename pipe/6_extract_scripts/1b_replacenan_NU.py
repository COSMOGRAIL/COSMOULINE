#
#    NOW LOOK AT THIS !
#
#    We will replace the zeroes in the sigma files prior to 
#    the psf construction.
#    superfast, superclean...
#
from astropy.io import fits
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import imgdb, settings, computer
from modules.variousfct import proquest, notify
from modules.kirbybase import KirbyBase

askquestions = settings['askquestions']
withsound = settings['withsound']

    

def isNaN(x):
    return x!=x
    
def replaceNaNinFile(filename, value):
    sigstars = fits.open(filename, mode='update')
    scidata = sigstars[0].data
    if True in isNaN(scidata):
        print("Yep, some work for me: ", 
              len(scidata[isNaN(scidata)]), 
              "pixels.")
    scidata[isNaN(scidata)] = value
    sigstars.flush()
    
def replacezeroes(filename, value):
    myfile = fits.open(filename, mode='update')
    scidata = myfile[0].data
    for x in range(len(scidata)):
        for y in range(len(scidata[0])):
            if scidata[x][y] < 1.0e-8:
                print("Nearly zero at ", x, y)
                scidata[x][y] = value
    myfile.flush()


def replaceNaN(objkey, objkeyflag, objdir):
    # remember where we started from:
    origdir = os.getcwd()
    # select the images to treat:
    db = KirbyBase(imgdb)
    images = db.select(imgdb, ['gogogo', 'treatme', objkeyflag], 
                              [True, True, True], 
                              returnType='dict')
    print("Number of images to treat :", len(images))
    proquest(askquestions)
    for i, image in enumerate(images):
        
        print(i+1, "/", len(images), ":", image['imgname'])
        imgobjdir = os.path.join(objdir, image['imgname'])
        
        os.chdir(imgobjdir)
        replaceNaNinFile("sig.fits", 1.0e-8)
        replacezeroes("sig.fits", 1.0e-7)
        os.chdir(origdir)
        
    notify(computer, withsound, f"I replaced NaN for {objkey}")

if __name__ == "__main__":
    from config import objkey, objkeyflag, objdir
    replaceNaN(objkey, objkeyflag, objdir)
