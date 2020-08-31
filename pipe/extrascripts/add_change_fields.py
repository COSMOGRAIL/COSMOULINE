execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from astropy.time import Time



print "This script is to add fields by hand... adapt the source !"
proquest(askquestions)


backupfile(imgdb, dbbudir, "addchangefield")

db = KirbyBase()

#db.addFields(imgdb, ['geomapscale:float'])

db.pack(imgdb) # always a good idea !


#sys.exit()

# int, str, bool

#images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict') # selects according to treatme
#images = db.select(imgdb, ['recno'], ['*'], returnType='dict') # selects all images
images = db.select(imgdb, ['gogogo'], [True], returnType='dict') # selects all 3 images

for image in images:
	name = image["rawimg"][-16:-5]
	mjd = float(name)
	print mjd
	t = Time(mjd, format='mjd')
	nbupdate = db.update(imgdb, ['recno'], [image['recno']], [mjd,mjd], ['mjd','mhjd'])
	if nbupdate == 1:
		print "updated"
	else :
		print "failed"

	t.format = "fits"
	print t.value[:-9]
	date = t.value[:-9]
	nbupdate = db.update(imgdb, ['recno'], [image['recno']], [date], ['datet'])
	if nbupdate == 1:
		print "updated"
	else :
		print "failed"

	t.format = 'jd'
	print t.value
	jd = t.value
	nbupdate = db.update(imgdb, ['recno'], [image['recno']], [str(jd)], ['jd'])
	if nbupdate == 1:
		print "updated"
	else :
		print "failed"


db.pack(imgdb)

sys.exit()


