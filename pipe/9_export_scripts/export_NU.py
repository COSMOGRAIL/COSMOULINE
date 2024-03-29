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
from config import imgdb, settings, pklfilepath, readmefilepath, \
                   pklgenericfilepath, dbcopyfilepath
from modules.variousfct import proquest, writepickle
from modules.kirbybase import KirbyBase

db = KirbyBase(imgdb)

xephemlens = settings['xephemlens']
lensName   = settings['lensName']
refimgname = settings['refimgname']
askquestions = settings['askquestions']

print("I am the only script that writes into your configdir.")
print("But I will try to be careful.")



########### The readme #############

readme = [f"This is the automatic readme file for\n{pklfilepath}\n"]

# We do only one select :
db = KirbyBase(imgdb)
images = db.select(imgdb, ['recno'], 
                          ['*'], 
                          sortFields=['setname', 'mjd'], 
                          returnType='dict')
mjdsortedimages = sorted(images, key=lambda k: k['mjd'])

readme.append(f"Target: {xephemlens}")

readme.append(f"Total: {len(images)} images")
beg, end = mjdsortedimages[0]['datet'], mjdsortedimages[-1]['datet']
readme.append(f"Time span: {beg} -> {end}")

telescopes = sorted(list(set([image["telescopename"] for image in images])))
setnames = sorted(list(set([image["setname"] for image in images])))

readme.append(f"Telescopes : {','.join(telescopes)}")
readme.append(f"setnames : {','.join(setnames)}")


readme.append(f"Ref image name : {refimgname} ")



fieldnames = db.getFieldNames(imgdb)
fieldtypes = db.getFieldTypes(imgdb)
fielddesc = [f"{fieldname} {fieldtype}" 
                for (fieldname, fieldtype) in zip(fieldnames, fieldtypes)]


deconvolutions = [fieldname[11:] 
                   for fieldname in fieldnames 
                     if fieldname.split("_")[0] == "decfilenum"]

deconvolutionsreadout = [fieldname[4:] 
                            for fieldname in fieldnames 
                               if (fieldname.split("_")[0] == "out")  
                                   and (fieldname.split("_")[-1] == "flux" 
                                   or   fieldname.split("_")[-1] == "int")]

readme.append("\nDeconvolutions :")
readme.extend(deconvolutions) 

readme.append("\nDeconvolution sources :")
readme.extend(deconvolutionsreadout)


renorms = [fieldname for fieldname in fieldnames if fieldname[0:6] == "renorm"]

readme.append("\nRenorms :")
readme.extend(renorms)


readmetxt = "\n".join(readme)
# print(f"Here is the readme text : \n\n{readmetxt}\n\n")

print("I will now write the files.")
proquest(askquestions)

readme.append("\nThe full list of fields :")
readme.extend(fielddesc)
readme.append("\n\n(end of automatic part)\n")
readmetxt = "\n".join(readme)


if os.path.exists(readmefilepath) \
    or os.path.exists(pklfilepath) \
    or os.path.exists(dbcopyfilepath):
	print("The files exist. I will overwrite them.")
	proquest(askquestions)
	if os.path.exists(readmefilepath):
		os.remove(readmefilepath)
	if os.path.exists(pklfilepath):
		os.remove(pklfilepath)
	if os.path.exists(pklgenericfilepath):
		os.remove(pklgenericfilepath)		
	if os.path.exists(dbcopyfilepath):
		os.remove(dbcopyfilepath)



out_file = open(readmefilepath, "w")
out_file.write(readmetxt)
out_file.close()
print(f"Wrote {readmefilepath}")

 # copy once the file with the date on its name...
writepickle(images, pklfilepath, verbose=True)
# and redoit using a generic name, for the automated reduction procedure...
writepickle(images, pklgenericfilepath, verbose=True) 

shutil.copy(imgdb, dbcopyfilepath)


print("Done!")
