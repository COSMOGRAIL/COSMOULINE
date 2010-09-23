def justreplace(inputstring, repdict):
	
	template = inputstring
	
	for key, value in repdict.iteritems():
		template = template.replace(key, value)
	
	return template

def justread(inputfilename):
	import sys
	import os
	
	infile = open(inputfilename, 'r')
	content = infile.read()
	infile.close()
	return content


#Try to use readmancat in variousfct, it's better	

#def readmancoords(mancatfile): # reads a man cat with format "id x y flux" and comments + blank lines
#	
#	import sys
#	import os
#	
#	print "WARNING THIS FUNCTION IS DEPRECATED"
#	
#	myfile = open(mancatfile, "r")
#	lines = myfile.readlines()
#	myfile.close
#	table=[]
#	for line in lines:
#		if line[0] == '#' or len(line) < 4:
#			continue
#		elements = line.split()
#		if len(elements) != 4:
#			print "Wrong format :", mancatfile
#			sys.exit()
#		starid = elements[0]
#		xpos = float(elements[1])
#		ypos = float(elements[2])
#		flux = float(elements[3])
#		table.append([starid, xpos, ypos, flux])
#	
#	print "I've read", len(table), "stars from", mancatfile
#	return table


def readouttxt(outtxtfile, nbimg): # function to read the out.txt written by deconv.exe
	import sys
	import os 	
 
	infile = open(outtxtfile, 'r')
	content = infile.readlines()
	nblines = len(content)
	print "Number of lines :", nblines
	infile.close()
	
	i = 0
	intpostable = []
	while i < nblines:
		line = content[i]
		if line.find("Nombre d")>=0:
			nbiter = line.split()[-1]
			if nbiter[0] == ":":
				nbiter = nbiter[1:]
			nbiter = int(nbiter)
			print "Number of iterations :", nbiter
			
		if line.find("  - Num")>=0:
			table = []
			for j in range(i+1, i+1+nbimg):
				values = map(float, content[j].split())
				table.append(values)
			intpostable.append(table)
			i = i+nbimg
		if line.find("* Valeurs finales de z1, z2, delta1 et delta2 :")>=0:
			zdeltatable = []
			for j in range(i+1, i+1+nbimg):
				values = map(float, content[j].split())
				zdeltatable.append(values)
			i = i+nbimg
			
		i = i+1
	
	return intpostable, zdeltatable
	
