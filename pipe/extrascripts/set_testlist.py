#
#    sets the testlist-flag according to the contents of the "testlist" file.
#    It's a bit long as we make this one foolproof...

import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import dbbudir, imgdb, settings, testlist
from modules.variousfct import proquest, readimagelist, mterror, backupfile
from modules.kirbybase import KirbyBase

db = KirbyBase(imgdb)  

askquestions = settings['askquestions']
setnames = settings['setnames']
refimgname_per_band = settings['refimgname_per_band']

# Read the testlist
testlisttxt = readimagelist(testlist) # a list of [imgname, comment]

# Check if it contains the reference image (you need this if you want to deconvolve)
for setname, refimgname in refimgname_per_band.items():
    # this is a simple list of the imgnames to update.
    testlistimgs = [image[0] for image in testlisttxt] 
    if refimgname not in testlistimgs:
        print(f"Reference image of band {setname} is not in your testlist.")
        print(f"That is: {refimgname}")
        print("It's a good idea to put it there... (at least for deconvolution)")
        print("(I will NOT add it by myself !)")
        proquest(True)

# Ask if OK
print("I will update the database for those %i images !"%len(testlistimgs)) 
proquest(askquestions)

# Check the input list for typos ...
# i.e. if all these images do exist in our database !
allimages = db.select(imgdb, ['recno'], ['*'], returnType='dict')
allnames = [image['imgname'] for image in allimages]

for imgname in testlistimgs :
    if imgname not in allnames:
        raise mterror("Image %s is not in the database !"%imgname)

# Now we check if the fields are in the database.
if "testlist" not in db.getFieldNames(imgdb) :
    print("Hmm, those fields are not in the database (what have you done???).",
          "I will add them.")
    proquest(askquestions)
    db.addFields(imgdb, ['testlist:bool', 'testcomment:str'])

# Ok, in this case we are ready.

# Make a backup
backupfile(imgdb, dbbudir, "updatetestlistflag")

db.update(imgdb, ['testlist'], ['*'], [False], ['testlist'])
for image in testlisttxt:
    print(image[0])
    nbupdate = db.update(imgdb, ['imgname'], 
                                [image[0]], 
                                [True, image[1]], 
                                ['testlist', 'testcomment'])
    if nbupdate == 1:
        print("updated")
    else:
        print("########### P R O B L E M ##########")
    
testimages = db.select(imgdb, ['testlist'], [True], returnType='dict')    

print("We have %i test-images in the database." % len(testimages))

db.pack(imgdb)
