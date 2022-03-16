#
#	Shows the full info available in the database for some images	
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *

db = KirbyBase()

# we get a list of all image names
namelist = [image[0] for image in db.select(imgdb, ['recno'], ['*'], ['imgname'])]

inname = input("Type an image name (or substring) to inspect (or just type 'ref'): ")

if inname == "ref":
	print("You want the reference image.")
	inname = refimgname
selectedlist = [image for image in namelist if inname in image]

if len(selectedlist) == 0:
	print("Sorry, no match.")
	sys.exit()

if len(selectedlist) > 1:
	print("This matches to %i images" % len(selectedlist))
	print("I will display full info for all of them")
	proquest(askquestions)

for name in selectedlist:

	imagedict = db.select(imgdb, ['imgname'], [name], returnType='dict')[0]
	
	print("- "*40)
	print(name)
	print("- "*40)

	for key, value in imagedict.items():
		print("   %24s : %12s"%(key, repr(value)))


sys.exit()
