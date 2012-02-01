#
#	stuff to export some fields of the database to rdb
#	In fact, to make it more general, we will just go from a 
#	collection of python lists of same lengths to columns of an rdb file.
#


from variousfct import *


def writerdb(columns, filename, writeheader=True, autoformat=True):
	"""
	If autoformat is True, I'll format some common columns a bit nicer.
	"""
	# columns = [{"name":string, "data":pythonlist}, ...], ordered as you want them to be in the rdb file.
	# filename = full path to the file to write.
	
	import csv
	import sys
	import os
	import copy
	
	
	# Just to be sure, we stat by checking if the columns all have the same length.
	lengths = map(lambda x : len(x["data"]), columns)
	if len(set(lengths)) != 1:
		raise mterror("Columns must all have the same length !")
	
	colnames = [column["name"] for column in columns]
	
	if 0 in map(len, colnames):
		raise mterror("C'mon, give a name to that poor column !")
	
	# Tests done.
	
	# We make a copy, as we might change the columns content :
	columns = copy.deepcopy(columns)
	#for column = columns:
	#	column["data"] = column["data"]
	
	if autoformat:
		for column in columns:
			# Stuff with high precision :
			if column["name"] in ["mhjd"] or "mag_" in column["name"]:
				column["data"] = map(lambda x: "%.6f" % (x), column["data"])
			elif "magerr_" in column["name"]:
				column["data"] = map(lambda x: "%.4f" % (x), column["data"])
			# Stuff with medium precision :
			elif column["name"] in ["fwhm", "elongation", "airmass", "normcoeff"]:
				column["data"] = map(lambda x: "%.3f" % (x), column["data"])
			# Stuff with low precision :
			elif column["name"] in ["relskylevel"]:
				column["data"] = map(lambda x: "%6.1f" % (x), column["data"])

	
	underline = ["="*n for n in map(len, colnames)]	
	data = zip(*[column["data"] for column in columns])
	
	#if os.path.isfile(filename):
	#	print "File exists. If you go on I will overwrite it."
	#	proquest(True)
	
	outfile = open(filename, "wb") # b needed for csv
	writer = csv.writer(outfile, delimiter="\t")
	
	
	if writeheader :
		writer.writerow(colnames)
		writer.writerow(underline)
	writer.writerows(data)
	
	outfile.close()
	
	print "Wrote %s" % (filename) 
	print "Column index - Label"
	print "\n".join([ "%12i - %s" % (coli, column["name"]) for (coli, column) in enumerate(columns)])
	
	
	
	
	
	
	
	


