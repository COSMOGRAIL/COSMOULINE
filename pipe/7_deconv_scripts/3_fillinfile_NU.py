#
#    write the input file in.txt and deconv.txt for the deconvolution
#
import numpy as np
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import imgdb, settings, configdir, deconv_template_filename,\
                   in_template_filename
from modules.variousfct import proquest, mcsname, mterror
from modules.kirbybase import KirbyBase
from modules.readandreplace_fct import justread, justreplace
from modules import star

askquestions = settings['askquestions']
workdir = settings['workdir']
decname = settings['decname']
decnormfieldname = settings['decnormfieldname']
decpsfnames = settings['decpsfnames']
decobjname = settings['decobjname']
refimgname = settings['refimgname']


# this script can be ran with an object to deconvolve as an argument.
# in this case, force the rebuild of all the keys
if len(sys.argv) == 2:
    decobjname = sys.argv[1]
    deckey  = f"dec_{decname}_{decobjname}_{decnormfieldname}_"
    deckey += "_".join(decpsfnames)
    ptsrccat = os.path.join(configdir, deckey + "_ptsrc.cat")
    decskiplist = os.path.join(configdir,deckey + "_skiplist.txt")
    deckeyfilenum = "decfilenum_" + deckey
    deckeynormused = "decnorm_" + deckey
    decdir = os.path.join(workdir, deckey)
    print("You are running the deconvolution on all the stars at once.")
    print("Current star : " + sys.argv[1])
else:
    from config import deckeyfilenum, ptsrccat, decdir, deckey
# else we import them from config as usual. 


db = KirbyBase()
# WARNING the sorting below is important !!!!!!!
images = db.select(imgdb, [deckeyfilenum], 
                          ['\d\d*'], 
                          returnType='dict', 
                          useRegExp=True, 
                          sortFields=[deckeyfilenum]) 

# We duplicate the ref image :
refimage = [image for image in images if image['imgname'] == refimgname][0] 
# This copy is important:
images.insert(0, refimage.copy()) 
# The duplicated ref image gets number 1:
images[0][deckeyfilenum] = mcsname(1)


nbimg = len(images)

print(f"We have {nbimg} images (ref image is duplicated).")


    # read params of point sources
try:
    ptsrc = star.readmancat(ptsrccat)
    nbptsrc = len(ptsrc)
    print("Number of point sources :", nbptsrc)


except:
    print("I haven't seen any point source catalogue in your configdir...")
    print("I can create it with the following input:")
    print(f"{decobjname}\t33\t33\t100000")
    proquest(askquestions)
    os.system(f"touch {ptsrccat}")
    cat = open(ptsrccat, 'w')
    cat.write(f"{decobjname}\t33\t33\t100000")
    cat.close()
    print("OK, done !")

    ptsrc = star.readmancat(ptsrccat)
    nbptsrc = len(ptsrc)
    print("Number of point sources :", nbptsrc)



proquest(askquestions)

# building deconv.txt
    
deconv_template = justread(deconv_template_filename)
deconvdict = {"$nbimg$": str(nbimg), "$nbptsrc$":str(nbptsrc)}
deconvtxt = justreplace(deconv_template, deconvdict)
deconvfile = open(os.path.join(decdir, "deconv.txt"), "w")
deconvfile.write(deconvtxt)
deconvfile.close()
print("Wrote deconv.txt")

# building in.txt

# int and pos of the sources
intandposblock = ""
print("Reformatted point sources :")
for i in range(nbptsrc):
    if ptsrc[i].flux < 0.0:
        err = "Please specify a positive flux for your point sources !"
        raise mterror(err)
    intandposblock = intandposblock + nbimg * (str(ptsrc[i].flux) + " ") + "\n"
    intandposblock+= str(2*ptsrc[i].x-0.5) + " " + str(2*ptsrc[i].y-0.5) + "\n"
    print(str(ptsrc[i].flux), str(2*ptsrc[i].x-0.5), str(2*ptsrc[i].y-0.5))
intandposblock    = intandposblock.rstrip("\n") # remove the last newline
    
# other params
otheriniblock = nbimg * "1.0 0.0 0.0 0.0\n"
otheriniblock = otheriniblock.rstrip("\n") # remove the last newline

in_template = justread(in_template_filename)
indict = {"$otheriniblock$": otheriniblock, "$intandposblock$": intandposblock}
intxt = justreplace(in_template, indict)
infile = open(os.path.join(decdir, "in.txt"), "w")
infile.write(intxt)
infile.close()
print("Wrote in.txt")




# We test the seeingpixels: 
# all values should be above 2, otherwise the dec code will crash:
testseeings = np.array([image["seeingpixels"] for image in images])
for image in images:
    print(image["imgname"], image["seeingpixels"])

if not np.all(testseeings>2.0):
    err = "I have seeinpixels <= 2.0, deconv.exe cannot deal with those."
    raise mterror(err)

fwhmtxt = "\n".join([f"{image['seeingpixels']:.4f}" for image in images])+"\n"
fwhmfile = open(os.path.join(decdir, "fwhm-des-G.txt"), "w")
fwhmfile.write(fwhmtxt)
fwhmfile.close()
print("Wrote fwhm-des-G.txt")



print(f"I've prepared the input files for {deckey}.")

print("Here they are, if you want to tweak them :")
print(os.path.join(decdir, "in.txt"))
print(os.path.join(decdir, "deconv.txt"))

    
    
