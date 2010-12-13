"""
Classes and functions around simulated Skymaker images
"""
import sys, os, shutil
from datetime import datetime, timedelta
#import variousfct
import pyfits
import skysim_sources

class Simimg:
	"""
	Stores all the settings to generate a Skymaker image
	"""
	
	def __init__(self, image_size=None, image_type=None, image_name=None, grid_size=None, image_header=None, gain=None, satur_level=None, readout_noise=None,
		exposure_time=None, mag_zeropoint=None, pixel_size=None, psf_type=None, psf_name=None, seeing_type=None, seeing_fwhm=None, aureole_radius=None,
		aureole_sb=None, psf_oversamp=None, psf_mapsize=None, trackerror_type=None, trackerror_maj=None, trackerror_min=None, trackerror_ang=None,
		m1_diameter=None, m2_diameter=None, arm_count=None, arm_thickness=None, arm_posangle=None, back_mag=None, sky_list=None):

		#--------------------------------- Image -------------------------------------
		self.image_name=image_name		# The name of the image
		self.image_size=image_size		# Width,[height] of the output frame
		self.image_type=image_type		# PUPIL_REAL,PUPIL_IMAGINARY,PUPIL_MODULUS,
							# PUPIL_PHASE,PUPIL_MTF,PSF_MTF,PSF_FULLRES,
							# PSF_FINALRES,SKY_NONOISE,SKY,GRID
							# or GRID_NONOISE
		self.grid_size=grid_size		# Distance between objects in GRID mode
		self.image_header=image_header		# File name or INTERNAL
		
		#-------------------------------- Detector -----------------------------------
		
		self.gain=gain				# gain (e-/ADU)
		self.satur_level=satur_level		# saturation level (ADU)
		self.readout_noise=readout_noise	# read-out noise (e-)
		self.exposure_time=exposure_time	# total exposure time (s)
		self.mag_zeropoint=mag_zeropoint	# magnitude zero-point ("ADU per second")
		
		#-------------------------------- Sampling -----------------------------------
		
		self.pixel_size=pixel_size		# pixel size in arcsec
		
		#---------------------------------- PSF --------------------------------------
		
		self.psf_type=psf_type			# INTERNAL or FILE
		self.psf_name=psf_name			# Name of the FITS image containing the PSF
		self.seeing_type=seeing_type		# (NONE, LONG_EXPOSURE or SHORT_EXPOSURE)
		self.seeing_fwhm=seeing_fwhm		# FWHM of seeing in arcsec (incl. motion)
		self.aureole_radius=aureole_radius	# Range covered by aureole (pix) 0=no aureole
		self.aureole_sb=aureole_sb		# SB (mag/arcsec2) at 1' from a 0-mag star
		self.psf_oversamp=psf_oversamp		# Oversampling factor / final resolution
		self.psf_mapsize=psf_mapsize		# PSF mask size (pixels): must be a power of 2
		self.trackerror_type=trackerror_type	# Tracking error model: NONE, DRIFT or JITTER
		self.trackerror_maj=trackerror_maj	# Tracking RMS error (major axis) (in arcsec)
		self.trackerror_min=trackerror_min	# Tracking RMS error (minor axis) (in arcsec)
		self.trackerror_ang=trackerror_ang	# Tracking angle (in deg, CC/horizontal)
		
		#----------------------------- Pupil features --------------------------------
		
		self.m1_diameter=m1_diameter		# Diameter of the primary mirror (in meters)
		self.m2_diameter=m2_diameter		# Obstruction diam. from the 2nd mirror in m.
		self.arm_count=arm_count		# Number of spider arms (0 = none)
		self.arm_thickness=arm_thickness	# Thickness of the spider arms (in mm)
		self.arm_posangle=arm_posangle		# Position angle of the spider pattern / AXIS1
		
		
		#--------------------------------- Signal ------------------------------------
		
		self.back_mag=back_mag			# background surface brightness (mag/arcsec2)
		
		#--------------------------------- stars on the field ------------------------------------
		
		self.sky_list=sky_list


def proquest():
	"""
	Asks the user if he wants to proceed. If not, exits python.
	
	"""
	answer = raw_input("Tell me, do you want to go on ? (yes/no) ")
	if answer[:3] != "yes":
		sys.exit("Ok, bye.")
	print ""


def write_images(imglist, simname="MySim", skypath="sky", workdir=".", skyconffile="config.sky"):
	"""
	Give me a list of Simimg objects, and I'll write the corresponding image files.
	imglist = list of Simimg objects
	simname = a name for your image set
	skypath = the path to skymaker
	workdir = a directory where I can write your images
	skyconffile = path of the default configuration file for skymaker
	Settings of the Simimg objects will supersede these default settings
	"""

	print "Simulation '%s' : %i images." % (simname, len(imglist))
	destdir = os.path.join(workdir, simname)
	print "I'll write them here : %s" % (destdir)
	if os.path.isdir(destdir):
		print "Ok, this simulation directory already exists. I will erase it..."
		proquest()
		shutil.rmtree(destdir)
	os.mkdir(destdir)

	pythondtstart = datetime.now()

	for i, image in enumerate(imglist):

		print "- " * 30
		print "%i/%i : %s" % (i+1, len(imglist), image.image_name)


		if image.image_name == None:
			imgfilename = "%i" % (i+1)
		else:
			imgfilename = image.image_name
			
		imgfilepath = os.path.join(destdir, "%s.fits" % imgfilename)
		sourcelistfilepath = os.path.join(destdir, "%s.inlist" % imgfilename)
		mancatfilepath = os.path.join(destdir, "%s.cat" % imgfilename)
		
		parameters = ""		# a string to write all the parameter to give to skymaker "-attr value -attr2 value2" except sky_list
	
		parameters += " -IMAGE_NAME %s" % imgfilepath 	#sky maker will save the img directly in the good directory		
	
		for attr, value in image.__dict__.iteritems():
			
			if attr == "image_name":
				continue
			
			if attr == "sky_list" and value != None:
				skysim_sources.write_sourcelist(sourcelistfilepath, value)
				skysim_sources.write_mancat(mancatfilepath, value)
				continue
				
			if attr == "image_size" and value != None:
				attr = attr.upper()
				parameters += " -%s %s,%s" %(attr, value[0], value[1])
				continue
				
	
			if value != None:
				attr = attr.upper()
				parameters += " -%s %s" %(attr, value)
		
		command = "%s %s -c config.sky %s" %(skypath, sourcelistfilepath, parameters)
		print command
		
		skymakerout = os.system(command)
		
		# We rewrite the DATE-OBS field
		# The timedelta ensures that all images will be a few seconds apart, in chronological order.
		pythondtimage = pythondtstart + timedelta(seconds = 60.0*i) 

		hdulist = pyfits.open(imgfilepath, mode = "update")
		hdulist[0].header.update("DATE-OBS", pythondtimage.strftime("%Y-%m-%dT%H%M%S"), "Tweaked simulation date")
		hdulist.flush()
	
	
	print "- " * 30
	print "Done."

