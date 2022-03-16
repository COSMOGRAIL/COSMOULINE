#
#	The aim is to combine the image per night before the deconvolution to see if that improves the deconvolution process.
#	It can be very usefull for faint image. 	
#
#	In this first part, we will put normalized images in a new directory and write the inputs of the combination (textfile containing the name of the image to combine).
# 	The database is also modified: we add a special field "combiname_num" which is a unique number that specify in which combination the image has been used (for exemple all the image with "combiname_num" = 1 have been combined together). The resulting combined image has a negativ "combiname_num" that refer to the images used in the combination (for exemple, a "combiname_num" of the combined image = -1 means that the images with "combiname_num" =1 have been combined) 
#	The combination will be done in the second script.


exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from pyraf import iraf
from kirbybase import KirbyBase, KBError
import shutil
from variousfct import *
from combibynight_fct import *
import time
from numpy import *
from headerstuff import *

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
	sumvals = float(sum(values))
	medvals = float(median(values))
	stddevvals = float(std(values))
	minvals = float(min(values))
	maxvals = float(max(values))
	meanvals = float(mean(values))
	
	return {'median': medvals, 'stddev': stddevvals, 'min': minvals, 'max': maxvals, 'mean':meanvals, 'sum':sumvals}


		

print("You want to create the input for the image combination per night of observation.")
print("Combiname = ", combiname)
proquest(askquestions)

backupfile(imgdb, dbbudir, "combine_" + combiname)

db = KirbyBase()

if thisisatest:
	print("This is a test : I will combine the images from the testlist, disregarding your criteria !")
	listimages = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
	imgrefdict = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')
else:
	listimages = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname', 'mjd'])
	imgrefdict = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')



if os.path.isdir(combidir):
	print("Ok, this combidir already exists. I will erase it...")
	proquest(askquestions)
	shutil.rmtree(combidir)
os.mkdir(combidir)

# Check if the combinamenumber is already in the database
combinamenum = combidirname +'_num'
if combinamenum not in db.getFieldNames(imgdb):
	db.addFields(imgdb, ['%s:int' % combinamenum])


groupedimages = groupbynights(listimages)

print("I have selected", len(listimages), "images.")
print("I recognized ", len(groupedimages), " observation nights")
proquest(askquestions)

infoofnights = []


imgrefdict = imgrefdict[0]	#so that we really have a dictonary and not a list

for j, images in enumerate(groupedimages):

	# formating a string of the observation date from julian date
	
	jdmed = values(images, "jd")['median']
	pythondtmed = DateFromJulianDay(jdmed)
	datenightobsmed = pythondtmed.strftime("%Y-%m-%d")
	
	jdmin = values(images, "jd")['min']
	pythondtmin = DateFromJulianDay(jdmin)
	datenightobsmin = pythondtmin.strftime("%Y-%m-%d")

	
	print("%i :  writing input for the night %s" %(j+1, datenightobsmin))
	
	if datenightobsmin is not datenightobsmed:
		combinightdir = os.path.join(combidir, datenightobsmin)		#directory that will contain the iraf input for the combination, the symlinks on the nonorm images and the images normalized to combine
	else:
		combinightdir = os.path.join(combidir, datenightobsmed)
	
	if os.path.isdir(combinightdir):	# if this happen, then look at the function groupbynights
		print("The directory already exists. It mean that 2 sets of images have the same date! It is not normal!")
		sys.exit()
	os.mkdir(combinightdir)	
	
	combilist = []	#list containing the normalized images to combine

	print("Normalizing images ...")

	for i, image in enumerate(images):
		
		# we give to the image use for the combination of this night a unic number that will correspond the combined image (update of the database)
		db.update(imgdb, ['recno'], [image['recno']], [j+1], [combinamenum])
		
		print(i+1, image['imgname'])
		
		ali = os.path.join(alidir, image['imgname'] + "_ali.fits")
		nonorm = os.path.join(combinightdir, image['imgname'] + "_ali.fits")
		norm = os.path.join(combinightdir, image['imgname'] + "_alinorm.fits")
		
		if os.path.isfile(nonorm):
			os.remove(nonorm)
		os.symlink(ali, nonorm)
		
		mycoeff = image[renormcoeff]
		
		if os.path.isfile(norm):
			os.remove(norm)
			
		iraf.imutil.imarith(operand1=nonorm, op="*", operand2=mycoeff, result=norm)
		
		combilist.append(os.path.join(combinightdir,image['imgname'] + "_alinorm.fits"))
		# Attention : we only append image names, not full paths !
		
	print("Done with normalizing")
	
	os.chdir(combinightdir)
	
	inputfiles = '\n'.join(combilist) + '\n'
	txt_file = open('irafinput.txt', 'w')
	txt_file.write(inputfiles)
	txt_file.close()
	
	
	# Gathering information for the groupdimage to add into the pickle
	
	print("\nGathering information for this groupdimage to add into a pickle...")
	
	
	combinumname = "combinum" 		# I attribute to each combined image a unic number to add into the database. That will help to identify which images I used for the combination
	
	listcoeff = [image[renormcoeff] for image in images]
	
	dbdict = {combinumname:-(j+1) , 'saturlvl': values(images, "satur_level")['sum'], 'skylevel': values(images, "skylevel")['sum'], 'telslon': images[0]['telescopelongitude'],'telslat': images[0]['telescopelatitude'],'telsele':images[0]['telescopeelevation'], 'gain': values(images, "gain")['median'], 'rdnoise': values(images, "readnoise")['median'], 'jd': jdmin, 'date': datenightobsmin, 'exptime': values(images, "exptime")['sum'], 'pixsize': imgrefdict['pixsize'], 'scfactor': imgrefdict['scalingfactor'], 'imgname': combidirname +'_'+ datenightobsmin, 'ncombine':len(images), 'listcoeff':listcoeff}
	
	
	infoofnights.append(dbdict) # In this case we build a big list to create a pickle
	
	print("Done. \n")


# Here we do a pickle of a list of dictionnaries
filepath = os.path.join(pipedir, 'fac_combi_scripts/' + 'info_temp.pkl')
writepickle(infoofnights, filepath)

db.pack(imgdb)

print("I finished to create inputs for all the observation nights")
