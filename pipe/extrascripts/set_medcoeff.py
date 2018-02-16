#
#	sets gogogo to False for images in the kicklist
#


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *

print "I will set medcoeff to 1 for all images."
# print imgkicklist

# imagestokick = readimagelist(imgkicklist)



proquest(askquestions)

backupfile(imgdb, dbbudir, "setmedcoeff")

db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict') # selects according to treatme
print "I will treat " + str(len(images)) + " images."
for image in images:
    print image['imgname']
    nbupdate = db.update(imgdb, ['gogogo','treatme'], [True, True], [1.0], ['medcoeff'])
    if nbupdate == 1:
        print "updated"
    else:
        print "# # # WARNING # # #"
        print "Image could not be updated. Perhaps not in database ?"

# images = db.select(imgdb, ['recno'], ['*'], returnType='dict')
# for image in images:
#     print image['medcoeff']
# demoted = db.select(imgdb, ['gogogo'], [False], ['imgname', 'seeing', 'nbralistars', 'geomaprms', 'whynot'], returnType='report')
# print demoted

# demoted = db.select(imgdb, ['gogogo'], [False], returnType='dict')
# print "Number of gogogo = False :", len(demoted)
#
db.pack(imgdb)
