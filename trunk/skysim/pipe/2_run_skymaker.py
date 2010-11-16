#
#	Runs skymaker to simulate images. A pickle containing the infos about the images to simulate is given to it. (the pickle is created by prepsimul.py)
#


execfile("./config.py")
from datetime import datetime, timedelta
import shutil
from variousfct import *
import asciidata

print "You want to simulate the set of images : ", simname 
proquest(askquestions)

filepath = os.path.join(pipedir, simname + '.pkl')
listimages = readpickle(filepath)	# this is a list of object simimg

nbrofimages = len(listimages)

print "I will simulate %s images." %nbrofimages
proquest(askquestions)

thissimdir = os.path.join(workdir, simname)
if os.path.isdir(thissimdir):
	print "Ok, this simulation directory already exists. I will erase it..."
	proquest(askquestions)
	shutil.rmtree(thissimdir)
os.mkdir(thissimdir)

starttime = datetime.now()

#the default parameters (the parameters that we tweak) of skymaker are written in the config.py but each image has specific set of parameters

config_filepath = os.path.join(pipedir, "config.sky")
sky_list = "sky_list.txt"
sky_list_filepath = os.path.join(pipedir, sky_list)
skymakerin = "config.sky"

#we simulate now the image one by one using skymaker
for i,image in enumerate(listimages):

	print "- " * 30
	print i+1, "/", nbrofimages, ":"

	
	# I write config.sky

	pythondtnow = datetime.now()
	imgname = simname + "_" + pythondtnow.strftime("%Y-%m-%dT%H%M%S")
	imgfilename = imgname + ".fits"		#the name of the simulate image
	imgfilepath = os.path.join(thissimdir, imgfilename)
	
	parameters = ""		# a string to write all the parameter to give to skymaker "-attr value -attr2 value2" except sky_list

	parameters += " -IMAGE_NAME %s" %imgfilename		

	for attr, value in image.__dict__.iteritems():
		if attr == "sky_list" and type(value) != None:
			value.writeto(sky_list_filepath)
		
		elif attr == "image_size" and type(value) != None:
			attr = attr.upper()
			parameters += " -%s %s,%s" %(attr, value[0], value[1])

		elif value != None:
			attr = attr.upper()
			parameters += " -%s %s" %(attr, value)
	
	command = "%s -c config.sky %s" %(sky_list, parameters)

	skymakerout = os.system(sky + " " + command)
	
	#saving the output simulated image and the star.list into the correct directory
	os.system("mv %s %s " %(imgfilename,thissimdir))
	star_list = imgname + ".list"
	os.system("mv %s %s " %(star_list,thissimdir))




#We delete the sky_list.txt to keep the directory clean
os.remove(sky_list_filepath)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

print "I'me done with the simulation. It took me %s" % timetaken



