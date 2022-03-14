# This is the first script.
# We add images to the database, read their headers, etc.
# If no database exists, we create one. 
# If not we add the images, after some test.

import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

import glob

from config import imgdb, dbbudir, settings
from modules.variousfct import backupfile
from modules.kirbybase import KirbyBase
from modules.variousfct import mterror, proquest
import modules.headerstuff as headfuncs

# We define some mandatory fields in the database :

minimaldbfields = ['imgname:str', 'treatme:bool', 'gogogo:bool', 'whynot:str', 
'testlist:bool', 'testcomment:str', 'telescopename:str', 'setname:str', 
'rawimg:str', 'scalingfactor:float', 'pixsize:float','date:str','datet:str',
'jd:str','mjd:float', 'telescopelongitude:str', 'telescopelatitude:str', 
'telescopeelevation:float', 'exptime:float','gain:float', 'readnoise:float',
'rotator:float', 'saturlevel:float', 'preredcomment1:str', 
'preredcomment2:str', 'preredfloat1:float', 'preredfloat2:float',
'filter:str', 'updating:bool']

setnames = settings['setnames']
rawdirs = settings['rawdirs']

# Function that selects the one that reads the header, 
# according to telescopename

def readheader(telescopename, rawimg, setname):
    if telescopename == "EulerC2":
        dbdictread = headfuncs.eulerc2header(rawimg, setname)
    elif telescopename == "EulerCAM":
        dbdictread = headfuncs.eulercamheader(rawimg, setname)
    elif telescopename == "Mercator":
        dbdictread = headfuncs.mercatorheader(rawimg, setname)
    elif telescopename == "Liverpool":
        dbdictread = headfuncs.liverpoolheader(rawimg, setname)
    elif telescopename == "MaidanakSITE":
        dbdictread = headfuncs.maidanaksiteheader(rawimg, setname)
    elif telescopename == "MaidanakSI":
        dbdictread = headfuncs.maidanaksiheader(rawimg, setname)
    elif telescopename == "Maidanak2k2k":
        dbdictread = headfuncs.maidanak2k2kheader(rawimg, setname)
    elif telescopename == "HCT":
        dbdictread = headfuncs.hctheader(rawimg, setname)
    elif telescopename == "HoLi":
        dbdictread = headfuncs.holiheader(rawimg, setname)
    elif telescopename == "SMARTSandicam":
        dbdictread = headfuncs.smartsandicamheader(rawimg, setname)
    elif telescopename == 'skysim':
        dbdictread = headfuncs.skysimheader(rawimg, setname)
    elif telescopename == "Maidanak_2.5k":
        dbdictread = headfuncs.Maidanak_2_5kheader(rawimg, setname)
    elif telescopename == "VST":
        dbdictread = headfuncs.VSTheader(rawimg, setname)
    elif telescopename == "VST_mosaic":
        dbdictread = headfuncs.VST_mosaic_header(rawimg, setname)
    elif telescopename == "VATT":
        dbdictread = headfuncs.VATTheader(rawimg, setname)
    elif telescopename == "LCO":
        dbdictread = headfuncs.LCOheader(rawimg, setname)
    elif telescopename == "NOT":
        dbdictread = headfuncs.Stancamheader(rawimg, setname)
    # from here ... not sure these headers are defined anymore.
    elif telescopename == 'FORS2':
        dbdictread = headfuncs.fors2header(rawimg, setname)
    elif telescopename == 'EFOSC2':
        dbdictread = headfuncs.efosc2header(rawimg, setname)
    elif telescopename == "WFI":
        dbdictread = headfuncs.wfiheader(rawimg, setname)
    elif telescopename == "GROND":
        dbdictread = headfuncs.grondheader(rawimg, setname)
    elif telescopename == "SDSS":
        dbdictread = headfuncs.sdssheader(rawimg, setname)
    elif telescopename == "GMOS":
        dbdictread = headfuncs.gmosheader(rawimg, setname)
    elif telescopename == "NOHEADER":
        dbdictread = headfuncs.noheader(rawimg, setname)
    elif telescopename == "PANSTARRS":
        dbdictread = headfuncs.PANSTARRSheader(rawimg, setname)
    elif telescopename == "SPECULOOS":
        dbdictread = headfuncs.SPECULOOSheader(rawimg, setname)
    elif telescopename == "UH2m2":
        dbdictread = headfuncs.UH2m2header(rawimg, setname)
    else:
        raise mterror("Unknown telescope.")    

    return dbdictread


db = KirbyBase(imgdb)


print("Here we go !")
for setname, rawdir in zip(setnames, rawdirs):
    print("You want to add/update the set ", 
          setname, 
          "to the database.")
    print(rawdir)
    
    if not os.path.isdir(rawdir):
        raise mterror("This directory does not exist!")
    fitsfiles = glob.glob(os.path.join(rawdir, "*.fits"))
    print("Number of images :", len(fitsfiles))
    fitslist = sorted([os.path.basename(filepath) for filepath in fitsfiles])
    
    proquest(settings['askquestions'])
    
    print("You did not forget to flip these images (if needed), right ?")
    proquest(settings['askquestions'])
    
    
    if os.path.isfile(imgdb):
    
        print("Database exists ! I will ADD these new images.")
        proquest(settings['askquestions'])
        backupfile(imgdb, dbbudir, "adding"+setname)
    
        # Add the updating field and set it to False, 
        # if not existing yet in the actual db
        currentfields = db.getFieldNames(imgdb)
        if not 'updating' in currentfields:
            db.addFields(imgdb, ['updating:bool'])
            # select all images:
            images = db.select(imgdb, ['recno'], ['*'], returnType='dict') 
            for image in images:
                db.update(imgdb, ['recno'], 
                                 [image['recno']], [False], ['updating'])
            db.pack(imgdb) # always a good idea !
    
        # We check if all the fields are there
        presentfields = db.getFieldNames(imgdb)
        mandatoryfields = [field.split(':')[0] for field in minimaldbfields]
        mandatoryfields.append('recno')
        if not set(mandatoryfields).issubset(set(presentfields)):
            err = "Your database misses mandatory fields! Change this and repeat."
            raise mterror(err)
        
        # We check if the setname is already used
        usedsetnames = [x[0] for x in db.select(imgdb, ['recno'], 
                                                       ['*'], ['setname'])]
        usedsetnameshisto = "".join(["{item:10}: {usedsetnames.count(item):4}\n" 
                                                    for item in set(usedsetnames)])
        print("In the database, we already have :")
        print(usedsetnameshisto)
        proquest(settings['askquestions'])
        if setname in usedsetnames:
            print("Your setname is already used. Would you like to update it ?")
            proquest(settings['askquestions'])
        
        # We get a list of the rawimg we have already in the db :
        knownrawimgs = [x[0] for x in db.select(imgdb, ['recno'], 
                                                       ['*'], ['rawimg'])]
        knownimgnames = [x[0] for x in db.select(imgdb, ['recno'], 
                                                        ['*'], ['imgname'])]
        
        # Ok, if we are here then we can insert our new images into the database.
        for i, fitsfile in enumerate(fitslist):
            print(i+1, fitsfile)
            rawimg = os.path.join(rawdir, fitsfile)
            
            dbdict = readheader(settings['telescopename'], rawimg, setname)
            
            # We check if this image already exists in the db. 
            # If yes, we just skip it.
            # For this we compare the "rawimg", that is the path of 
            # the image file and the "imgname", that contains the setname
                    
            if dbdict["rawimg"] in knownrawimgs \
                    or dbdict["imgname"] in knownimgnames:
                print("I already have this one !",
                      "(-> I skip it without updating anything)")
                continue
    
            if settings['update']:
                dbdict["updating"] = True  # for updating databases
            else:
                dbdict["updating"] = False
    
            # We have to insert image by image into our database.
            db.insert(imgdb, dbdict)
    
    
    else:
        print("A NEW database will be created.")
        proquest(settings['askquestions'])
        db.create(imgdb, minimaldbfields)
    
        table = []
        for i, fitsfile in enumerate(fitslist):
            print(i+1, "/", len(fitslist), " : ", fitsfile)
            rawimg = os.path.join(rawdir, fitsfile)    
            
            dbdict = readheader(settings['telescopename'], rawimg, setname)
            dbdict["updating"] = False
            #  always False when the database does not exists yet...
            
            
            table.append(dbdict)
            # In this case we build a big list for batch insertion.
    
    
        # Here we do a "batch-insert" of a list of dictionnaries
        db.insertBatch(imgdb, table)

db.pack(imgdb)  # to erase the blank lines

print("Ok, Done.")
print("If you work with several telescopes or sets,",
      "you might want to change the treatme-flags at this point.")
print("Or more likely: update the settings and run this again,",
      "to add further images from another directory/telescope.")



