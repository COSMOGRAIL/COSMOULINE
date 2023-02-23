#    
#    this script is here to just extract the object to deconvolve
#    it uses the new extract.exe programm, 
#    but I separated this from the psf construction.
#    So I will throw away psf extraction.
#    
#    the important think here is objkey !    
#
#    Again, this script is a bit long, as it performs some checks
#    to make sure that the dear user does not make mistakes.
#

import shutil
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import dbbudir, imgdb, settings, extract_template_filename, \
                    alidir, extractexe, computer
from modules.variousfct import backupfile, proquest, readmancat, mterror,\
                               notify, copyorlink
from modules.kirbybase import KirbyBase
from modules.readandreplace_fct import justread, justreplace

askquestions = settings['askquestions']
withsound = settings['withsound']
workdir = settings['workdir']
uselinks = settings['uselinks']
refimgname_per_band = settings['refimgname_per_band']


def extractObj(objkey, objcoordcat, objdir, objkeyflag, objcosmicskey):
    """
    extracts stamps for the object objkey. The other arguments are the 
    associated catalogs, directories, flags, etc. These are defined in
    config.py

    """
    db = KirbyBase(imgdb)
    
    print("objkey =", objkey)
        
    # read the position of the object to extract
    
    objcoords = readmancat(objcoordcat)
    if len(objcoords) != 1: 
        raise mterror("...one extraction at a time please!")
    # We do not care about the name that you gave to this source...
    # In fact we do not care about the source at all,
    # just want to know what part of the image to extract.
    objcoordtxt = "%7.2f %7.2f\n" % (objcoords[0]['x'], objcoords[0]['y'])
    print("coords = ", objcoordtxt)
    proquest(askquestions)
    
    
    # select images to extract from
    
    usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], 
                                                ['*'], ['setname'])])
    for setname in usedsetnames:
        bandrefimage = refimgname_per_band[setname]
        if settings['thisisatest'] :
            print("This is a test run.")
            images = db.select(imgdb, ['gogogo','treatme','testlist','setname'], 
                                      [True, True, True, setname], 
                                      returnType='dict', 
                                      sortFields=['setname', 'mjd'])
        else :
            images = db.select(imgdb, ['gogogo', 'treatme', 'setname'], 
                                      [True, True, setname], 
                                      returnType='dict', 
                                      sortFields=['setname', 'mjd'])
        
        nbrofimages = len(images)
        
        print("I will extract from", nbrofimages, "images.")
        print("Please understand that I update the database.")
        print("Thus, do not run me in parallel !")
        proquest(askquestions)
        
        # Before any change, we backup the database.
        backupfile(imgdb, dbbudir, "extract_" + objkey)
        
        
        # We check if this obj already exists :
        
        if os.path.isdir(objdir):    # start from empty directory
            print("Ok, this objdir already exists:")
            print(objdir)
            
            if objkeyflag not in db.getFieldNames(imgdb) :
                err = "...but your corresponding objkey is not in the database!"
                raise mterror(err)
            
            print("I will add or rebuild images within this objdir.")
            proquest(askquestions)
        else :
            
            print("I will create a NEW objdir/objkey:")
            print(objdir)
            proquest(askquestions)
            if objkeyflag not in db.getFieldNames(imgdb):
               db.addFields(imgdb, 
                            [f'{objkeyflag}:bool', f'{objcosmicskey}:int'])
            else:
                err = "...funny: the objkey was in the DB!"
                err += " Please clean objdir and objkey!"
                raise mterror(err)
            os.mkdir(objdir)
            
        
        
        # read the template files
        extract_template = justread(extract_template_filename)
        
        origdir = os.getcwd()
        n = 0
        for image in images:
            n += 1
            print(n, "/", len(images), ":", image['imgname'])
        
            
            imgobjdir = os.path.join(objdir, image['imgname'])
            
            if os.path.isdir(imgobjdir):
                print("Deleting existing stuff.")
                shutil.rmtree(imgobjdir)
            os.mkdir(imgobjdir)
            
            os.symlink(os.path.join(alidir, f"{image['imgname']}_ali.fits"), 
                       os.path.join(imgobjdir, "in.fits"))
            
            
            extrdict = {"$imgname$": "in.fits", "$nbrpsf$": "1", 
                        "$gain$": str(image['gain']), 
                        "$stddev$": str(image['stddev'])}
            extrdict.update([["$psfstars$", "200.0 200.0"]])
            extrdict.update([["$lenscoord$", objcoordtxt]])
            
            extracttxt = justreplace(extract_template, extrdict)
            extractfilepath = os.path.join(imgobjdir, "extract.txt")
            with open(extractfilepath, "w") as extractfile:
                extractfile.write(extracttxt)
            
            os.chdir(imgobjdir)
            os.system(extractexe)
            # we remove the one psf we have extracted:
            os.remove("g001.fits")        
            os.remove("sig001.fits")
            os.chdir(origdir)
            
            if os.path.exists(os.path.join(imgobjdir, "in.fits")):
                os.remove(os.path.join(imgobjdir, "in.fits"))
            
            # and we update the database with a "True" for field psfkeyflag :
            db.update(imgdb, ['recno'],  [image['recno']], 
                             [True, -1], [objkeyflag, objcosmicskey])
            
        db.pack(imgdb)
        
        notify(computer, withsound, 
               f"Master, I've extracted a source from {n} images.")
        
        
        if bandrefimage in [img["imgname"] for img in images]:
            
            imgobjdir = os.path.join(objdir, bandrefimage)
            sourcepath = os.path.join(imgobjdir, "g.fits")
            destname = f"{setname}_{objkey}_ref_input.fits"
            destpath = os.path.join(workdir, destname)
            copyorlink(sourcepath, destpath, uselinks)
            
            print("We linked the extraction from the reference image here:")
            print(destpath)    
        else:
            warn = f"Warning: the reference image of {setname} "
            warn += "was not in your selection !"
            print(warn)


if __name__ == "__main__":
    from config import objkey, objcoordcat, objdir, objkeyflag, objcosmicskey
    
    extractObj(objkey, objcoordcat, objdir, objkeyflag, objcosmicskey)