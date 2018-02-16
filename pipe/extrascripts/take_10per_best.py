execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import os

# Read the list
list = os.path.join(configdir, "list_10per.txt")
dirname = os.path.join(workdir,"10per_best")
psfdir = os.path.join(workdir,"psf_"+psfname)
psfpngdir = os.path.join(workdir,"psf_"+psfname+"_png")
listtxt = readimagelist(list) # a list of [imgname, comment]

# Check if it contains the reference image (you need this if you want to deconvolve)
listimgs = [image[0] for image in listtxt] # this is a simple list of the imgnames to update.

print listimgs

if not os.path.exists(dirname):
    os.mkdir(dirname)
    os.mkdir(dirname + "/stamp")
    os.mkdir(dirname + "/psf")

for image in listimgs :
    print image
    os.system("cp -r " + workdir + "/obj_lens/"+image +" " + dirname + "/stamp/")
    os.system("cp -r " + psfdir + "/" + image + " " + dirname + "/psf/")
    os.system("cp -r " + psfpngdir + "/" + image + ".png " + dirname + "/psf/")
