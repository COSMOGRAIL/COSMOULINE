#
#	sets the testlist-flag according to the contents of the "testlist" file.
#	It's a bit long as we make this one foolproof...

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *


# Read the testlist
testlisttxt = readimagelist(testlist) # a list of [imgname, comment]

# Check if it contains the reference image (you need this if you want to deconvolve)
testlistimgs = [image[0] for image in testlisttxt] # this is a simple list of the imgnames to update.
if refimgname not in testlistimgs:
	print "Reference image is not in your testlist."
	print "It's a good idea to put it there... (at least for deconvolution)"
	print "refimgname =", refimgname
	print "(I will NOT add it by myself !)"
	proquest(askquestions)

# Ask if OK
print "I will update the database for those %i images !"% len(testlistimgs) 
proquest(askquestions)

# Check the input list for typos ...i.e. if all these images do exist in our database !
db = KirbyBase()
allimages = db.select(imgdb, ['recno'], ['*'], returnType='dict')
allnames = [image['imgname'] for image in allimages]

for imgname in testlistimgs :
	if imgname not in allnames:
		raise mterror("Image %s is not in the database !"%imgname)

# Now we check if the fields are in the database.
if "testlist" not in db.getFieldNames(imgdb) :
	print "Hmm, those fields are not in the database (what have you done ???). I will add them."
	proquest(askquestions)
	db.addFields(imgdb, ['testlist:bool', 'testcomment:str'])

# Ok, in this case we are ready.

# Make a backup
backupfile(imgdb, dbbudir, "updatetestlistflag")

for image in testlisttxt:
	print image[0]
	nbupdate = db.update(imgdb, ['imgname'], [image[0]], [True, image[1]], ['testlist', 'testcomment'])
	if nbupdate == 1:
		print "updated"
	else:
		print "########### P R O B L E M ##########"
	
# get the total number (including previous ones... ) of test images.
testimages = db.select(imgdb, ['testlist'], [True], returnType='dict')	

print "We have %i test-images in the database." % len(testimages)
#notify(computer, withsound, "We have %i test-images in the database." % len(testimages))

db.pack(imgdb)
