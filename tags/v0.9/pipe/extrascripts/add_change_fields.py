execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *



print "This script is to add fields by hand... adapt the source !"
proquest(askquestions)


backupfile(imgdb, dbbudir, "addchangefield")

db = KirbyBase()

db.addFields(imgdb, ['geomapscale:float'])

db.pack(imgdb) # always a good idea !


sys.exit()

# int, str, bool

#images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict') # selects according to treatme
images = db.select(imgdb, ['recno'], ['*'], returnType='dict') # selects all images
#images = db.select(imgdb, ['setname'], ['Mer1'], returnType='dict') # selects all Mer1 images

nbrofimages = len(images)
for i,image in enumerate(images):
	print i, "/", nbrofimages, ":", image['imgname']
	db.update(imgdb, ['recno'], [image['recno']], [10], ['maxalistars'])

db.pack(imgdb) # always a good idea !

