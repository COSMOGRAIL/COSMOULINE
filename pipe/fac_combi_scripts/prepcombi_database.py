#
#	The aim is to combine the image per night before the deconvolution to see if that improves the deconvultion process
#	
#	In this first part, we will put normalized images in a new directory and modify the database to have
#	The combination will be done in the second script.

print "I should add smthg to support the treat me mecanism!"

execfile("../config.py")
from pyraf import iraf
from kirbybase import KirbyBase, KBError
import shutil
from variousfct import *
from combibynight_fct import *
import time
from numpy import *

##############################################
# A function make some statistic on a groupe of image for a particular field of the database
# in : a list of image (a list of dict) and a key (field on the database. Must refere to a float or int)
# out : a dict with the fields and their values
###############################################

def values(listofimg, key):	# stats of the values within the given nights

	from numpy import array, median, std, min, max, mean
	medvals= 0
	stddevvals= 0
	minvals= 0
	maxvals= 0
	meanvals = 0
	
	values = array([float(image[key]) for image in listofimg])
	medvals = float(median(values))
	stddevvals = float(std(values))
	minvals = float(min(values))
	maxvals = float(max(values))
	meanvals = float(mean(values))
	
	return {'median': medvals, 'stddev': stddevvals, 'min': minvals, 'max': maxvals, 'mean':meanvals}


##############################################
# A function to read the information of an images group and to get what to write in the combidatabase about the combinated image
# in : a dictionnary of the field you want to add and an images group
# out : a dict with the fields and their values
###############################################

def readinfobynight(groupedimage, dictfield):
	
	returndict = dictfield
	
	for (key, value) in dictfield.iteritems():
		
		if value is "str" and key is not "imgname":
			returndict[key] = groupedimage[0][key]	# this is completly arbitrary
		elif value is "int":
			returndict[key] = values(groupedimage, key)['median']
		elif value is "float":
			returndict[key] = values(groupedimage, key)['median']
		elif key is "imgname":
			returndict[key] = groupedimage[0]["setname"] +"_combi_" + groupedimage[0]["date"]
		elif key is "testlist":
			returndict[key] = False
		elif key is "treatme":
			returndict[key] = True
		elif key is "gogogo":
			returndict[key] = True
	
	return returndict
		

print "You want to create the input for the image combination per night of observation. All the images you want to have for the light curves should be added to the database before to lauch this script. \n I do not support the TreatMe system because I rewrite a database!"
proquest(askquestions)


db = KirbyBase()

if thisisatest:
	print "This is a test : I will combine the images from the testlist, disregarding your criteria !"
	listimages = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
else:
	listimages = db.select(imgdb, ['gogogo'], [True], returnType='dict', sortFields=['setname', 'mjd'])

print "I have selected", len(listimages), "images."
proquest(askquestions)


if os.path.isdir(combidir):
	print "Combidir already exists. There is something to erase..."
	proquest(askquestions)
	shutil.rmtree(combidir)
os.mkdir(combidir)


groupedimages = groupbynights(listimages)

#################################
#
#################################

# I get the field of the current database manually, only the ones I find important to have in the combidatabase

dbfieldcombidict = {
'setname':'str',
'medcoeff':'float',                                                                             
'sigcoeff':'float',                                                                              
'spancoeff':'float',                                                                              
'stddev':'float',                                                                              
'maxlens':'float',                                                                              
'sumlens':'float',
'testlist':'bool',
'testcomment':'str',
'skylevel':'float',
'prealistddev':'float',
'seeing':'float',
'ell':'float',
'seeingpixels':'float',
'hjd':'str',
'mhjd':'float',
'calctime':'str',
'alt':'float',
'az':'float',
'airmass':'float',
'moonpercent':'float',
'moondist':'float',
'sundist':'float',
'sunalt':'float',
'imgname':'str',
'treatme':'bool',
'gogogo':'bool',
'whynot':'str',
'telescopename':'str',
'scalingfactor':'float',
'pixsize':'float',
'date':'str',
'datet':'str',
'jd':'str',
'mjd':'float',
'telescopelongitude':'str',
'telescopelatitude':'str',
'telescopeelevation':'float',
'gain':'float',
'readnoise':'float',
'rotator':'float',
'preredcomment1':'str',
'preredcomment2':'str',
'preredfloat1':'float',
'preredfloat2':'float'}

dbfieldcombilist = []

for (key, value) in dbfieldcombidict.iteritems():
	field = key +':'+ value
	dbfieldcombilist.append(field)


if os.path.isfile(combinightimgdb):
	print "Database exists ! I will delete it."
	proquest(askquestions)
	os.remove(combinightimgdb)
	
#print "A NEW database will be created."
#proquest(askquestions)

db.create(combinightimgdb, dbfieldcombilist)

table = []	#list containing the information to add to the database 


for j, images in enumerate(groupedimages):
	
	datenightobs = images[0]["date"]	# maybe to put jd or mjd. It has to be one univoc per observation night
	
	print "%i :  writing input for the night %s" %(j+1, datenightobs)
	
	combinightdir = os.path.join(combidir, datenightobs)	#directory that will contain the iraf input for the combination, the symlinks on the nonorm images and the images normalized to combine
	
	if os.path.isdir(combinightdir):
		print "The directory already exits. It mean that 2 set of images have the same date! It is not normal!"
		sys.exit()
	os.mkdir(combinightdir)	
	
	combilist = []	#list containing the normalized images to combine

	print "Normalizing images ..."

	for i, image in enumerate(images):
		print i+1, image['imgname']
		
		ali = os.path.join(alidir, image['imgname'] + "_ali.fits")
		nonorm = os.path.join(combinightdir, image['imgname'] + "_ali.fits")
		norm = os.path.join(combinightdir, image['imgname'] + "_alinorm.fits")
		
		if os.path.isfile(nonorm):
			os.remove(nonorm)
		os.symlink(ali, nonorm)
		
		mycoeff = image['medcoeff']
		
		if os.path.isfile(norm):
			os.remove(norm)
			
		iraf.imutil.imarith(operand1=nonorm, op="*", operand2=mycoeff, result=norm)
		
		combilist.append(image['imgname'] + "_alinorm.fits")
		# Attention : we only append image names, not full paths !
		
	print "Done with normalizing"
	
	os.chdir(combinightdir)
	
	inputfiles = '\n'.join(combilist) + '\n'
	txt_file = open('irafinput.txt', 'w')
	txt_file.write(inputfiles)
	txt_file.close()
	
	# Gathering information for the groupdimage to add into the combindatabase
	
	print "\nGathering information for this groupdimage to add into the combidatabase..."
	
	
	dbdict = readinfobynight(images, dbfieldcombidict)
	
	
	table.append(dbdict) # In this case we build a big list for batch insertion
	
	print dbdict
	print "Done. \n"



# Here we do a "batch-insert" of a list of dictionnaries
db.insertBatch(combinightimgdb,table)
db.pack(combinightimgdb)

print "I finished to create inputs for all the observation nights"
