#
#	we mainly call the kirbybase validation function,
#	to see if everything is ok in our holy database.
#	(plus we check the number of images in the database)
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *


database = imgdb
#database = "/home/epfl/tewes/DECONV/J1001/work/database_corrupt.dat"



print("- "*40)
print("Checking number of entries ...")

f = open(database, 'r')
lines = f.readlines()
f.close()

headnbr = int(lines[0].split("|")[0])
nbroflines = len(lines) - 1
nbrofdifflines = len(set([int(x.split("|")[0]) for x in lines[1:]]))
maxrecno = max([int(x.split("|")[0]) for x in lines[1:]])

if (headnbr != nbroflines or headnbr != nbrofdifflines or headnbr != maxrecno) :
	print("\n\nError in number/numerotation of entries !!!\n\n")
	print("header :", headnbr)
	print("lines :", nbroflines)
	print("recnos :", nbrofdifflines)
	print("max recno :", maxrecno)

print("Done.")

print("- "*40)

print("Checking number of fields per line ...")

nbroffields = len(lines[0].split("|")) - 2
for line in lines[1:]:
	n = len(line.split("|"))
	if n != nbroffields:
		print("\n\nWrong number of fields in line :")
		print(line)

print("Done.")


print("- "*40)

print("Checking field types ...")
db = KirbyBase(imgdb)
output = db.validate(database)

if len(output) == 0:
	print("All entries are correct, my dear master.")
else:
	print("\n\nBummer !\n\n")
	for line in output:
		print(line)

print("Done.")
sys.exit()


