#
#	sets treatme to True/False for the images you want
#	Syntax: if column1=column2 then set column 4 to column 3
#	Example: if setname = 1 then set treatme to false.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *


print "This script is to change the treatme flags... adapt the source !"
proquest(askquestions)


backupfile(imgdb, dbbudir, "treatmeupdate")
db = KirbyBase()

# We do not have to select images first: directly update with a criteria !

n = db.update(imgdb, ['imgname'], ['1_cutout_rings.v3.skycell.0837.079.wrp.g.55274.46227'], [True], ['gogogo'])
# n = db.update(imgdb, ['imgname'], ['3_ECAM.2011-05-31T07:47:14.000'], [True], ['gogogo'])

#n = db.update(imgdb, ['setname'], ['3'], [True], ['treatme'])

#n = db.update(imgdb, ['recno'], ['*'], [False], ['treatme']) #	there is a bug, this does not seem to work :-(


#n = db.update(imgdb, ['treatme'], [False], [True], ['treatme'])

#n = db.update(imgdb, ['seeingpixels'], ['>-100'], [True], ['treatme'])

#n = db.update(imgdb, ['imgname'], [refimgname], [True], ['treatme'])


print "Number of updates : %i" % n

# And do not forget to pack afterwards.
db.pack(imgdb)








# The VERY VERY BAD AND SLOW way was :

#images = db.select(imgdb, ['recno'], ['*'], returnType='dict')
#for image in images:
#	if image['setname'] == "Mer2":
#		treatme = True
#	else:
#		treatme = False
#	db.update(imgdb, ['imgname'], [image['imgname']], [treatme], ['treatme'])
#	
#
#db.pack(imgdb)
