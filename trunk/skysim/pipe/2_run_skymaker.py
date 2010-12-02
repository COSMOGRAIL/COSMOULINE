#
#	Runs skymaker to simulate images. A pickle containing the infos about the images to simulate is given to it. (the pickle is created by prepsimul.py)
#


execfile("./config.py")
from datetime import datetime, timedelta
import shutil
from variousfct import *
from generate_skylist_fcts import *
import pyfits

print "You want to simulate the set of images : ", simname 
proquest(askquestions)

filepath = os.path.join(workdir, simname + '.pkl')
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

	
	#to use the time for the name of the image and for the DATE-OBS
	pythondtnow = datetime.now()
	delay = i
	dt = timedelta(seconds = delay) 
	pythondtnow = pythondtnow + dt


	#imgname = simname + "_" + pythondtnow.strftime("%Y-%m-%dT%H%M%S")
	
	
	if image.image_name == None:
		imgname = simname + "_%i" %(i+1)
	else:
		imgname = image.image_name

	imgfilename = imgname + ".fits"		#the name of the simulate image
	imgfilepath = os.path.join(thissimdir, imgfilename)
	
	parameters = ""		# a string to write all the parameter to give to skymaker "-attr value -attr2 value2" except sky_list

	parameters += " -IMAGE_NAME %s" %imgfilepath 	#sky maker will save the img directly in the good directory		

	for attr, value in image.__dict__.iteritems():
		if attr == "sky_list" and type(value) != None:
			writeto(sky_list_filepath, value)		# I write the skylist.txt
		
		elif attr == "image_size" and type(value) != None:
			attr = attr.upper()
			parameters += " -%s %s,%s" %(attr, value[0], value[1])

		elif value != None:
			attr = attr.upper()
			parameters += " -%s %s" %(attr, value)
	
	command = "%s -c config.sky %s" %(sky_list, parameters)

	skymakerout = os.system(sky + " " + command)
	
	# Modifying the header of the image freshly simulated
	
	hdulist = pyfits.open(imgfilepath, mode = "update")
	hdulist[0].header.update("DATE-OBS", pythondtnow.strftime("%Y-%m-%dT%H%M%S"), "the date of creation of the image")
	hdulist.flush()

	#saving the output simulated image and the star.list into the correct directory
	#shutil.move(imgfilename, thissimdir)
	#star_list = imgname + ".list"
	#shutil.move(star_list,thissimdir)




#We delete the sky_list.txt and the pickle to keep the directory clean
os.remove(sky_list_filepath)

print "\nDo you want to remove the pickle used to lunch the simulation? (Say 'no' if you plan to relunch this script with the same parameters) : "
proquest(askquestions)

os.remove(filepath) #the pickle to delete

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

print "I'm done with the simulation. It took me %s" % timetaken



