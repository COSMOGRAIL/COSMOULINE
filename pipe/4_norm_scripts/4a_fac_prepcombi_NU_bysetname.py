#
#	The aim is to combine some of the best images using the normalization coeffs
#	just calculated.
#
#	In this first part, we will put normalized images in a new directory
#	The combination will be done in the second script.


execfile("../config.py")
from pyraf import iraf
from kirbybase import KirbyBase, KBError
import shutil
from variousfct import *
import time

print "Name of combination: %s" % combibestname

combidir = os.path.join(workdir, combibestkey)

db = KirbyBase()
if thisisatest:
    print "This is a test : I will combine the images from the testlist, disregarding your criteria !"
    images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict',
                       sortFields=['setname', 'mjd'])
else:
    images = db.select(imgdb, ['gogogo', 'treatme', 'seeing', 'ell', 'medcoeff', 'stddev', 'setname'],
                       [True, True, '< %f' % combibestmaxseeing, '< %f' % combibestmaxell,
                        '< %f' % combibestmaxmedcoeff, '< %f' % combibestmaxstddev, setname], returnType='dict',
                       sortFields=['setname', 'mjd'])

print "I have selected", len(images), "images."
proquest(askquestions)

if os.path.isdir(combidir):
    print "There is something to erase..."
    proquest(askquestions)
    shutil.rmtree(combidir)
os.mkdir(combidir)

combilist = []
print "Normalizing images ..."

for i, image in enumerate(images):
    print i + 1, image['imgname'], image['seeing'], image['ell'], image['medcoeff'], image['sigcoeff']

    ali = os.path.join(alidir, image['imgname'] + "_ali.fits")
    nonorm = os.path.join(combidir, image['imgname'] + "_ali.fits")
    norm = os.path.join(combidir, image['imgname'] + "_alinorm.fits")

    if os.path.isfile(nonorm):
        os.remove(nonorm)
    os.symlink(ali, nonorm)

    mycoeff = image['medcoeff']
    if os.path.isfile(norm):
        os.remove(norm)
    iraf.imutil.imarith(operand1=nonorm, op="*", operand2=mycoeff, result=norm)

    combilist.append(image['imgname'] + "_alinorm.fits")
# Attention : we only append image names, not full paths !


os.chdir(combidir)

inputfiles = '\n'.join(combilist) + '\n'
txt_file = open('irafinput.txt', 'w')
txt_file.write(inputfiles)
txt_file.close()

print "Done."



