exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
import rdbexport
import variousfct
import datetime


print("I am the only script that writes into your configdir.")
print("But I will try to be careful.")



############ Building the filenames ##############

now = datetime.datetime.now()
datestr = now.strftime("%Y-%m-%d")
configstr = os.path.basename(os.path.normpath(configdir))
filename = "%s_%s" % (datestr, configstr)

readmefilepath = os.path.join(configdir, filename + "_readme.txt")
pklfilepath = os.path.join(configdir, filename + "_db.pkl")
pklgenericfilepath = os.path.join(configdir, "%s_db.pkl" % configstr)
dbcopyfilepath = os.path.join(configdir, filename + "_db.dat")


print("My basename : %s" % (filename))



########### The readme #############

readme = ["This is the automatic readme file for\n%s\n" %  pklfilepath]

# We do only one select :
db = KirbyBase()
images = db.select(imgdb, ['recno'], ['*'], sortFields=['setname', 'mjd'], returnType='dict')
mjdsortedimages = sorted(images, key=lambda k: k['mjd'])

readme.append("Target : %s" % xephemlens)

readme.append("Total : %i images" % (len(images)))
readme.append("Time span : %s -> %s" % (mjdsortedimages[0]["datet"], mjdsortedimages[-1]["datet"]))

telescopes = sorted(list(set([image["telescopename"] for image in images])))
setnames = sorted(list(set([image["setname"] for image in images])))

readme.append("Telescopes : %s" % ",".join(telescopes))
readme.append("Setnames : %s" % ",".join(setnames))


readme.append("Ref image name : %s " % refimgname)



fieldnames = db.getFieldNames(imgdb)
fieldtypes = db.getFieldTypes(imgdb)
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



"""

usedsetnames = map(lambda x : x[0], db.select(imgdb, ['recno'], ['*'], ['setname']))
gogogotrue = map(lambda x : x[0], db.select(imgdb, ['gogogo'], [True], ['setname']))
usedsetnameshisto = "".join(["%10s : %4i images (%4i with gogogo  == True)\n"%(item, usedsetnames.count(item), gogogotrue.count(item)) for item in sorted(list(set(usedsetnames)))])

print "- "*40
print "Image sets summary :"
print usedsetnameshisto.rstrip("\n")

treatmetrue = map(lambda x : x[0], db.select(imgdb, ['treatme'], [True], ['setname']))
usedsetnameshisto = [(item, usedsetnames.count(item), treatmetrue.count(item)) for item in sorted(list(set(usedsetnames)))]

print "- "*40
print "treatme flag summary :"
for item in usedsetnameshisto:
	if item[1] == item[2]:
		print "%10s : "%item[0] + "will all be treated (except gogogo == False)."
	elif item[1] != item[2] and item[2] != 0:
		print "%10s : "%item[0] + "will be partially treated (", item[2], "among", item[1], ") ???"
	elif item[2] == 0:
		print "%10s : "%item[0] + "will be skipped."
	else :
		print "I have a big bad problem with", item[0]

print "- "*40

treatmetrue = map(lambda x : x[0], db.select(imgdb, ['treatme','gogogo'], [True, True], ['setname']))


print "Number of images to treat that have gogogo == True :", len(treatmetrue)
print "Total number of images :", len(usedsetnames)
print "Images with gogogo == True :", len(gogogotrue)
"""


readmetxt = "\n".join(readme)
print("Here is the readme text : \n\n%s\n\n" % (readmetxt))

print("I will now write the files.")
variousfct.proquest(askquestions)

readme.append("\nThe full list of fields :")
readme.extend(fielddesc)
readme.append("\n\n(end of automatic part)\n")
readmetxt = "\n".join(readme)


if os.path.exists(readmefilepath) or os.path.exists(pklfilepath) or os.path.exists(dbcopyfilepath):
	print("The files exist. I will overwrite them.")
	variousfct.proquest(askquestions)
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
print("Wrote %s" % readmefilepath)

variousfct.writepickle(images, pklfilepath, verbose=True) # copy once the file with the date on its name...
variousfct.writepickle(images, pklgenericfilepath, verbose=True) # and redoit using a generic name, for the automated reduction procedure...

shutil.copy(imgdb, dbcopyfilepath)


print("Done !")
