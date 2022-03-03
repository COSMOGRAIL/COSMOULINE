#
#	We erase the fields testlist and testcomment.
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *


print("I will completely reset the fields testlist and testcomment.")
proquest(askquestions)

backupfile(imgdb, dbbudir, "testlistreset")

db = KirbyBase(imgdb)

if "testlist" in db.getFieldNames(imgdb) :
	db.dropFields(imgdb, ['testlist', 'testcomment'])

db.addFields(imgdb, ['testlist:bool', 'testcomment:str'])

db.pack(imgdb) # always a good idea !
print("Done.")

