import os
import glob

fitsdir = "rassemblement/"
dfitsout = os.popen("dfits rassemblement/c_e_*.fits | fitsort OBJECT")
liste = dfitsout.readlines()

found_obj = set()

for line in liste[1:]:
	elements = line.split()
	found_obj.add(elements[1])
	

print "Objects I've found :"
print found_obj


for obj in found_obj:
	os.system("mkdir " + obj)

for line in liste[1:]:
	elements = line.split()
	filename = elements[0]
	objname = elements[1]
	os.system("mv " + elements[0] + " " + objname + "/.")


exit()



