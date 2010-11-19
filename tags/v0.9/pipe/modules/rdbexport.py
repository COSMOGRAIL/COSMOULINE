#
#	stuff to export some fields of the database to rdb
#	In fact, to make it more general, we will just go from a 
#	collection of python lists of same lengths to columns of an rdb file.
#
#	Malte, 2008
#

from variousfct import *


def writerdb(columns, filename):
	# columns = [{"name":string, "data":pythonlist}, ...], ordered as you want them to be in the rdb file.
	# filename = full path to the file to write.
	
	import csv
	import sys
	import os
	
	# Just to be sure, we stat by checking if the columns all have the same length.
	lengths = map(lambda x : len(x["data"]), columns)
	if len(set(lengths)) != 1:
		raise mterror("Columns must all have the same length !")
	
	colnames = [column["name"] for column in columns]
	
	if 0 in map(len, colnames):
		raise mterror("C'mon, give a name to that poor column !")
	
	
	underline = ["="*n for n in map(len, colnames)]	
	data = zip(*[column["data"] for column in columns])
	
	if os.path.isfile(filename):
		print "File exists. If you go on I will overwrite it."
		proquest(True)
	
	outfile = open(filename, "wb") # b needed for csv
	writer = csv.writer(outfile, delimiter="\t")
	
	
	writer.writerow(colnames)
	writer.writerow(underline)
	writer.writerows(data)
	
	
	outfile.close()


