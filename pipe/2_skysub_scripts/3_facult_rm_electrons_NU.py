
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
import glob

# We select the images to treat :
db = KirbyBase()

print('I will simply remove all the orignial images (converted to electrons and hence copied) from the alidir.')
print('This will save some disk space, now that images are skysubtracted...')
print("Soft links would not be removed.")

db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')

print("I will try to delete %i images." % len(images))
proquest(askquestions)
for i, image in enumerate(images):

	print("%i : %s" % (i+1, image["imgname"]))
	filepath = os.path.join(alidir, image["imgname"] + ".fits")
	if os.path.isfile(filepath):
		os.remove(filepath)
	else:
		print("Hmm, no such file.")
	
print("Done.")
	

