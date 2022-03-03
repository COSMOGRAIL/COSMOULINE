exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError

db = KirbyBase(imgdb)

currentfields = db.getFieldNames(imgdb)
currenttypes = db.getFieldTypes(imgdb)

for i, field in enumerate(currentfields):
	print("%30s  %8s" % (field, currenttypes[i]))
	
print("These are", len(currentfields), "fields.")
