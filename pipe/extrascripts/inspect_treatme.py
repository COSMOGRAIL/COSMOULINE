#
#	A little script to inspect the status quo of the setnames and treatme flag
#	Does not change anything in the database or elsewhere.
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *

db = KirbyBase()

usedsetnames = [x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])]
gogogotrue = [x[0] for x in db.select(imgdb, ['gogogo'], [True], ['setname'])]
usedsetnameshisto = "".join(["%10s : %4i images (%4i with gogogo  == True)\n"%(item, usedsetnames.count(item), gogogotrue.count(item)) for item in sorted(list(set(usedsetnames)))])

print("- "*40)
print("Image sets summary :")
print(usedsetnameshisto.rstrip("\n"))

treatmetrue = [x[0] for x in db.select(imgdb, ['treatme'], [True], ['setname'])]
usedsetnameshisto = [(item, usedsetnames.count(item), treatmetrue.count(item)) for item in sorted(list(set(usedsetnames)))]

print("- "*40)
print("treatme flag summary :")
for item in usedsetnameshisto:
	if item[1] == item[2]:
		print("%10s : "%item[0] + "will all be treated (except gogogo == False).")
	elif item[1] != item[2] and item[2] != 0:
		print("%10s : "%item[0] + "will be partially treated (", item[2], "among", item[1], ") ???")
	elif item[2] == 0:
		print("%10s : "%item[0] + "will be skipped.")
	else :
		print("I have a big bad problem with", item[0])

print("- "*40)

treatmetrue = [x[0] for x in db.select(imgdb, ['treatme','gogogo'], [True, True], ['setname'])]


print("Number of images to treat that have gogogo == True :", len(treatmetrue))
print("Total number of images :", len(usedsetnames))
print("Images with gogogo == True :", len(gogogotrue))



print("- "*40)
sys.exit()
