#
#	sets gogogo to False for images in the kicklist
#


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *


print "I will set gogogo to False for all images written in the kicklist :"
print imgkicklist

imagestokick = readimagelist(imgkicklist)

print "Number of images in that list :", len(imagestokick)

proquest(askquestions)


backupfile(imgdb, dbbudir, "imgkickgogogoFalse")

db = KirbyBase()
#images = db.select(imgdb, ['recno'], ['*'], returnType='dict')


for image in imagestokick:
	print image[0]
	if image[0] == refimgname:
		print "1) Do not be rude."
		print "2) Eat your soup."
		print "3) Do not try to remove the reference image !!!!!"
		db.pack(imgdb)
		sys.exit()
	nbupdate = db.update(imgdb, ['imgname'], [image[0]], [False, image[1]], ['gogogo', 'whynot'])
	if nbupdate == 1:
		print "updated"
	else:
		print "# # # WARNING # # #"
		print "Image could not be updated. Perhaps not in database ?"
	

#demoted = db.select(imgdb, ['gogogo'], [False], ['imgname', 'seeing', 'nbralistars', 'geomaprms', 'whynot'], returnType='report')	
#print demoted

demoted = db.select(imgdb, ['gogogo'], [False], returnType='dict')	
print "Number of gogogo = False :", len(demoted)


db.pack(imgdb)
