#execfile("../config.py")

import os
import shutil
import sys

# to get access to all our modules without installing anything :
sys.path.append("../modules")

from kirbybase import KirbyBase, KBError
import rdbexport
import variousfct
import datetime


print "I am a special version, if you just want to translate an old db into a pkl."
print "I write my files in the current directory."
print "You have to configure me..."



configstr = "HS2209"
databasepath = "/Users/mtewes/Desktop/HS2209_database.dat" 


############ Building the filenames ##############

now = datetime.datetime.now()
datestr = now.strftime("%Y-%m-%d")

filename = "%s_%s" % (datestr, configstr)

configdir = "."
readmefilepath = os.path.join(configdir, filename + "_readme.txt")
pklfilepath = os.path.join(configdir, filename + "_db.pkl")

print "My basename : %s" % (filename)



########### The readme #############

readme = ["This is the automatic readme file for\n%s\n" %  pklfilepath]

# We do only one select :
db = KirbyBase()
images = db.select(databasepath, ['recno'], ['*'], sortFields=['setname', 'mjd'], returnType='dict')
mjdsortedimages = sorted(images, key=lambda k: k['mjd'])

readme.append("Target : %s" % configstr)

readme.append("Total : %i images" % (len(images)))
readme.append("Time span : %s -> %s" % (mjdsortedimages[0]["datet"], mjdsortedimages[-1]["datet"]))

telescopes = sorted(list(set([image["telescopename"] for image in images])))
setnames = sorted(list(set([image["setname"] for image in images])))

readme.append("Telescopes : %s" % ",".join(telescopes))
readme.append("Setnames : %s" % ",".join(setnames))


#readme.append("Ref image name : %s " % refimgname)



fieldnames = db.getFieldNames(databasepath)
fieldtypes = db.getFieldTypes(databasepath)
fielddesc = ["%s %s" % (fieldname, fieldtype) for (fieldname, fieldtype) in zip(fieldnames, fieldtypes)]


deconvolutions = [fieldname[11:] for fieldname in fieldnames if fieldname.split("_")[0] == "decfilenum"]

deconvolutionsreadout = [fieldname[4:] for fieldname in fieldnames if (fieldname.split("_")[0] == "out") and ( fieldname.split("_")[-1] == "flux" or fieldname.split("_")[-1] == "int")]

readme.append("\nDeconvolutions :")
readme.extend(deconvolutions)

readme.append("\nDeconvolution sources :")
readme.extend(deconvolutionsreadout)


renorms = [fieldname for fieldname in fieldnames if fieldname[0:6] == "renorm"]

readme.append("\nRenorms :")
readme.extend(renorms)



readmetxt = "\n".join(readme)
print "Here is the readme text : \n\n%s\n\n" % (readmetxt)

print "I will now write the files."
#variousfct.proquest(askquestions)

readme.append("\nThe full list of fields :")
readme.extend(fielddesc)
readme.append("\n\n(end of automatic part)\n")
readmetxt = "\n".join(readme)


if os.path.exists(readmefilepath) or os.path.exists(pklfilepath):
	print "The files exist. I will overwrite them."
	variousfct.proquest(askquestions)
	if os.path.exists(readmefilepath):
		os.remove(readmefilepath)
	if os.path.exists(pklfilepath):
		os.remove(pklfilepath)



out_file = open(readmefilepath, "w")
out_file.write(readmetxt)
out_file.close()
print "Wrote %s" % readmefilepath

variousfct.writepickle(images, pklfilepath, verbose=True)

