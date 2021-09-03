

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
import star


# Select images to treat
db = KirbyBase()

#images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')
images = db.select(imgdb, ['recno'], ["*"], returnType='dict')

nbrofimages = len(images)
print("Number of images to treat :", nbrofimages)
proquest(askquestions)

# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, "tweak")

for image in images:
	if image["telescopename"] == "EulerCAM":
		
		print(image["imgname"])
		db.update(imgdb, ['recno'], [image['recno']], {'scalingfactor': 0.89767829371})


db.pack(imgdb) # to erase the blank lines
print("Done")
