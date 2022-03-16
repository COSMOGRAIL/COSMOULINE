#
#	removes some fields from the database. makes a backup first.
#	you can give substrings of the fields to remove (typically if you want to remove "a deconvolution" give the decname), 
#	and all fields that match will be removed.
#	


exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *

remove = input("Type a field substring you want to remove : ")

db = KirbyBase()
currentfields = db.getFieldNames(imgdb)
currenttypes = db.getFieldTypes(imgdb)

fieldstoremove = []
for i, field in enumerate(currentfields):
	if field.find(remove) > -1:
		fieldstoremove.append([field, currenttypes[i]])

print("Fields that will be removed :")	
for field in fieldstoremove:
	print("%30s  %8s" % (field[0], field[1]))
print("These are", len(fieldstoremove), "fields.")

answer = input("Type GO to proceed. ")

if answer[:2] == "GO":
	backupfile(imgdb, dbbudir, "removing_"+remove)
	for field in fieldstoremove:
		db.dropFields(imgdb, [field[0]])
	db.pack(imgdb)
	print("Ok, they are all gone.")
else:
	print("Wrong answer, I did nothing.")


db.pack(imgdb) # always a good idea !
