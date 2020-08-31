execfile("../config.py")
import os,sys
import glob
from kirbybase import KirbyBase, KBError
from variousfct import *
from headerstuff import *
from readandreplace_fct import *
import numpy as np
import star
import shutil

#if not update:
#	raise mterror("update keyword not set to True !")

# This one is going to be tricky. And long

print "I will update the database with new images in set %s, telescope %s from %s" %(setname, telescopename, rawdir)
print ""
db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname', 'mjd'])
nbrofimages = len(images)
print "Number of images to treat :", nbrofimages

# lensdecpaths = None
lensdecpaths = ["dec_backfull_lens_renorm_adgjlnrvwxy_aegijk"] # put here the name of the lens deconvolutions you want to update

if not lensdecpaths == None:
	print "You want to update the following lens deconvolutions:"
	for decpath in lensdecpaths:
		print decpath
	print 'Note that I will update only ONE renormcoeff at the time, the one that is in your settings !'
	print 'I am not idiot-proof yet, so BE CAREFUL HERE !!!'
	proquest(True)
else:
	proquest(askquestions)

os.chdir('../7_deconv_scripts')

# Deconvolve each star with the new images
if 1:
	for renormsource in renormsources:

		# start by creating a temporary configuration file with the deconvolution keywords needed...
		# OH GOD THIS IS SO UGLY :O

		infos = renormsource[0].split('_')

		file = open(os.path.join(configdir,'deconv_config_update.py'), 'w')
		file.write('import os\n\n')
		file.write("configdir = '%s'\n " % configdir)
		file.write("\ndecname = %s" % "'"+infos[1]+"'")
		file.write("\ndecobjname = %s" % "'"+infos[2]+"'")
		file.write("\ndecnormfieldname = %s" % "'"+infos[3]+"'")
		file.write("\ndecpsfnames = %s" % '['+', '.join(["'"+decpsfname+"'" for decpsfname in infos[4:]])+']')
		file.write("\n\ndeckey = '%s'" % renormsource[0])
		file.write("\nptsrccat = os.path.join(configdir, deckey + '_ptsrc.cat')")
		file.write("\ndecskiplist = os.path.join(configdir, deckey + '_skiplist.txt')")
		file.write("\ndeckeyfilenum = 'decfilenum_' + deckey")
		file.write("\ndeckeypsfused = 'decpsf_' + deckey")
		file.write("\ndeckeynormused = 'decnorm_' + deckey")
		file.write("\ndecdir = os.path.join(workdir, deckey)")
		file.close()

		# Now I simply can rexececute the scripts on the whole set of images.

		# Before erasing the psfdir, I should grab the previous config files used:
		# ptsrc.cat stays in configdir, nothing to do...
		# must alter in.txt with stupid parameters
		# must alter deconv.txt with the new number of images
		# must rewrite fwhm-des-G.txt

		inpath = os.path.join(workdir, renormsource[0], 'in.txt')
		deconvpath = os.path.join(workdir, renormsource[0], 'deconv.txt')
		fwhmpath = os.path.join(workdir, renormsource[0], 'fwhm-des-G.txt')

		for path in [inpath, deconvpath, fwhmpath]:
			os.system('cp %s %s' % (path, os.path.join(workdir, 'updating_'+os.path.basename(path))))
			pass


		# I could save some time running 1 and 2 only on the updating images but the gain is 1-2 min. per star -- don't care
		# Note that we don't run 0 on stars - we want to compute the coeff for all the images !
		os.system('python 1_prepfiles.py')
		os.system('python 2_applynorm_NU.py')

		# Instead of 3, I simply move back or change wisely the config files previously backuped:
		execfile(os.path.join(configdir, 'deconv_config_update.py'))

		allimages = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=[deckeyfilenum])
		refimage = [image for image in allimages if image['imgname'] == refimgname][0]
		allimages.insert(0, refimage.copy())
		images[0][deckeyfilenum] = mcsname(1)
		nbimg = len(allimages)

		ptsrc = star.readmancat(ptsrccat)
		nbptsrc = len(ptsrc)

		# alter in.txt

		in_backuped = open(os.path.join(workdir, 'updating_'+os.path.basename(inpath)), 'r').readlines()
		new_in_backuped = open(inpath, 'w')

		toreplace = []
		for ind, line in enumerate(in_backuped):
			if line[0] not in ['|', '-'] and in_backuped[ind-1][0] == '-':
				indstart = ind
				for i in np.arange(len(in_backuped))[ind:]:
					if in_backuped[i][0] == '-':
						indend = i-1
						break
				if not indend <=indstart:
					toreplace.append([indstart, indend])

		# int and pos of the sources : first bunch of lines that does not start with | or -
		intandposblock = ""
		print "Reformatted point sources :"
		for i in range(nbptsrc):
			if ptsrc[i].flux < 0.0 :
				raise mterror("Please specify a positive flux for your point sources !")
			intandposblock = intandposblock + nbimg * (str(ptsrc[i].flux) + " ") + "\n"
			intandposblock = intandposblock + str(2*ptsrc[i].x-0.5) + " " + str(2*ptsrc[i].y-0.5) + "\n"

		# other params : second bunch of lines
		otheriniblock = nbimg * "1.0 0.0 0.0 0.0\n"

		# and apply the modifs. in reverse order, to avoid messing up the line numbers...
		for ind in np.arange(len(in_backuped))[toreplace[1][0]+1: toreplace[1][1]+1][::-1]:
			in_backuped.pop(ind)
		in_backuped[toreplace[1][0]] = otheriniblock

		for ind in np.arange(len(in_backuped))[toreplace[0][0]+1: toreplace[0][1]+1][::-1]:
			in_backuped.pop(ind)
		in_backuped[toreplace[0][0]] = intandposblock

		for line in in_backuped:
			new_in_backuped.write(line)
		new_in_backuped.close()

		# alter deconv.txt
		deconv_backuped = open(os.path.join(workdir, 'updating_'+os.path.basename(deconvpath)), 'r').readlines()
		new_deconv_backuped = open(deconvpath, 'w')
		for ind, line in enumerate(deconv_backuped):
			if ind==3: # ugly as well. Do NOT change the shape of deconv.txt... (it is not intented to be changed anyway)
				line = deconv_backuped[ind] = '|' + line[1:].split('|')[0] + '|%i\n' % int(nbimg)
			new_deconv_backuped.write(line)
		new_deconv_backuped.close()

		# rewrite fwhm-des-G.txt
		# We test the seeingpixels : all values should be above 2, otherwise the dec code will crash :
		testseeings = np.array([image["seeingpixels"] for image in allimages])
		if not np.all(testseeings>2.0):
			raise mterror("I have seeinpixels <= 2.0, deconv.exe cannot deal with those.")
		fwhmtxt = "\n".join(["%.4f" % image["seeingpixels"] for image in allimages]) + "\n"
		fwhmfile = open(fwhmpath, "w")
		fwhmfile.write(fwhmtxt)
		fwhmfile.close()


		# And now the rest of the deconv procedure
		os.system('python 4_deconv_NU.py')
		os.system('python 5a_decpngcheck_NU.py')
		os.system('python 6_readout.py')



	# I need to recompute the normalisation coefficient with these new values:
	os.chdir('../8_renorm_scripts')
	os.system('python 1a_renormalize.py')
	os.system('python 1b_report_NU.py')
	os.system('python 2_plot_star_curves_NU.py')
	os.system('python 4_fac_merge_pdf_NU.py')


# That being done, I can get back to the lens now
# I do it simple, I update all the dec_*_lens_* I find in the datadir, except dec_best

os.chdir('../7_deconv_scripts')

if lensdecpaths==None:
	lensdecpaths = glob.glob(os.path.join(workdir, "dec_*_lens_*"))
	lensdecpaths = [path for path in lensdecpaths if os.path.isdir(path) and not "png" in path and not "best" in path]

else:
	lensdecpaths = [os.path.join(workdir, decpath) for decpath in lensdecpaths]
	for decpath in lensdecpaths:
		if not os.path.isdir(decpath):
			print decpath, " does not exists ! Check your lensdecpaths !!"
			sys.exit()

#This is pretty much the same than above.
if 1:
	for abspath in lensdecpaths:

		infos = os.path.basename(abspath).split('_')
		try :
			r_index = infos.index('renorm')
			n_fieldname = infos[r_index] + "_" + infos[r_index+1]
		except:
			print "You don't have the key word 'renorm' in your renorm name ! I might get it wrong here !"
			n_fieldname = infos[-2]

		try :
			obj_index = infos.index("lens")
			if obj_index > 2 :
				print "Arf you choose a decname with '_', that was a bad idea ! But I can still live with it."
				deconvname = ""
				for i in range(1,obj_index+1):
					deconvname+=infos[i]
					if not i == obj_index:
						deconvname+="_"
			elif obj_index == 2 :
				deconvname = infos[obj_index-1]

			else :
				print "There is something strange here, I prefer to stop."
				print "Name of your deconv name : ", abspath
				sys.exit()

		except:
			print "I'm not deconvolving a lens, alles gut !"
			obj_index = 2
			deconvname = infos[obj_index-1]



		# still ugly...

		file = open(os.path.join(configdir,'deconv_config_update.py'), 'w')
		file.write('import os\n\n')
		file.write("configdir = '%s'\n " % configdir)
		file.write("\ndecname = %s" % "'"+deconvname+"'")
		file.write("\ndecobjname = %s" % "'"+infos[obj_index]+"'")
		file.write("\ndecnormfieldname = %s" % "'"+n_fieldname+"'")
		file.write("\ndecpsfnames = %s" % "['"+infos[-1]+"']")
		file.write("\n\ndeckey = '%s'" % os.path.basename(abspath))
		file.write("\nptsrccat = os.path.join(configdir, deckey + '_ptsrc.cat')")
		file.write("\ndecskiplist = os.path.join(configdir, deckey + '_skiplist.txt')")
		file.write("\ndeckeyfilenum = 'decfilenum_' + deckey")
		file.write("\ndeckeypsfused = 'decpsf_' + deckey")
		file.write("\ndeckeynormused = 'decnorm_' + deckey")
		file.write("\ndecdir = os.path.join(workdir, deckey)")
		file.close()
		# Now I simply can rexececute the scripts on the whole set of images.

		# Before erasing the psfdir, I should grab the previous config files used:
		# ptsrc.cat stays in configdir, nothing to do...
		# must alter in.txt with stupid parameters
		# must alter deconv.txt with the new number of images
		# must rewrite fwhm-des-G.txt
		# for the lens, I should also grab the previous background used...

		inpath = os.path.join(abspath, 'in.txt')
		deconvpath = os.path.join(abspath, 'deconv.txt')
		fwhmpath = os.path.join(abspath, 'fwhm-des-G.txt')

		for path in [inpath, deconvpath, fwhmpath]:
			os.system('cp %s %s' % (path, os.path.join(workdir, 'updating_'+os.path.basename(path))))
			pass

		# backup the background
		deconv_backuped = open(os.path.join(workdir, 'updating_'+os.path.basename(deconvpath)), 'r').readlines()
		for ind, line in enumerate(deconv_backuped):
			if ind==46:
				back_name = os.path.join(abspath,line.split('|')[-1])
				back_name = back_name.split('\n')[0]

		try :
			shutil.copy(back_name, os.path.join(workdir, 'updating_back.fits'))
		except:
			print back_name
			print "There is no background to backup, is this a deconvolution without backgound ??? "
			proquest(askquestions)

		# I could save some time running 1 and 2 only on the updating images but the gain is 1-2 min. per star -- don't care
		if 0: #makeautoskiplist
			os.system('python 0_facult_autoskiplist_NU.py')

		os.system('python 1_prepfiles.py')
		os.system('python 2_applynorm_NU.py')

		# Instead of 3, I simply move back or change wisely the config files previously backuped:
		execfile(os.path.join(configdir, 'deconv_config_update.py'))
		# first, the background:
		os.system('mv %s %s' % (os.path.join(workdir, 'updating_back.fits'), os.path.join(abspath, back_name)))

		allimages = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=[deckeyfilenum])
		refimage = [image for image in allimages if image['imgname'] == refimgname][0]
		allimages.insert(0, refimage.copy())
		images[0][deckeyfilenum] = mcsname(1)
		nbimg = len(allimages)

		ptsrc = star.readmancat(ptsrccat)
		nbptsrc = len(ptsrc)

		# alter in.txt

		in_backuped = open(os.path.join(workdir, 'updating_'+os.path.basename(inpath)), 'r').readlines()
		new_in_backuped = open(inpath, 'w')

		toreplace = []
		for ind, line in enumerate(in_backuped):
			if line[0] not in ['|', '-'] and in_backuped[ind-1][0] == '-':
				indstart = ind
				for i in np.arange(len(in_backuped))[ind:]:
					if in_backuped[i][0] == '-':
						indend = i-1
						break
				if not indend <=indstart:
					toreplace.append([indstart, indend])

		# int and pos of the sources : first bunch of lines that does not start with | or -
		intandposblock = ""
		print "Reformatted point sources :"
		for i in range(nbptsrc):
			if ptsrc[i].flux < 0.0 :
				raise mterror("Please specify a positive flux for your point sources !")
			intandposblock = intandposblock + nbimg * (str(ptsrc[i].flux) + " ") + "\n"
			intandposblock = intandposblock + str(2*ptsrc[i].x-0.5) + " " + str(2*ptsrc[i].y-0.5) + "\n"

		# other params : second bunch of lines
		otheriniblock = nbimg * "1.0 0.0 0.0 0.0\n"

		# and apply the modifs. in reverse order, to avoid messing up the line numbers...
		for ind in np.arange(len(in_backuped))[toreplace[1][0]+1: toreplace[1][1]+1][::-1]:
			in_backuped.pop(ind)
		in_backuped[toreplace[1][0]] = otheriniblock

		for ind in np.arange(len(in_backuped))[toreplace[0][0]+1: toreplace[0][1]+1][::-1]:
			in_backuped.pop(ind)
		in_backuped[toreplace[0][0]] = intandposblock

		for line in in_backuped:
			new_in_backuped.write(line)
		new_in_backuped.close()

		# alter deconv.txt
		new_deconv_backuped = open(deconvpath, 'w')
		for ind, line in enumerate(deconv_backuped):
			if ind==3: # ugly as well. Do NOT change the shape of deconv.txt... (it is not intented to be changed anyway)
				line = deconv_backuped[ind] = '|' + line[1:].split('|')[0] + '|%i\n' % int(nbimg)
			new_deconv_backuped.write(line)
		new_deconv_backuped.close()

		# rewrite fwhm-des-G.txt
		# We test the seeingpixels : all values should be above 2, otherwise the dec code will crash :
		testseeings = np.array([image["seeingpixels"] for image in allimages])
		if not np.all(testseeings>2.0):
			raise mterror("I have seeinpixels <= 2.0, deconv.exe cannot deal with those.")
		fwhmtxt = "\n".join(["%.4f" % image["seeingpixels"] for image in allimages]) + "\n"
		fwhmfile = open(fwhmpath, "w")
		fwhmfile.write(fwhmtxt)
		fwhmfile.close()


		# And now the rest of the deconv procedure
		os.system('python 4_deconv_NU.py')
		os.system('python 5a_decpngcheck_NU.py')
		os.system('python 6_readout.py')


	print "Finally done...ugh..."

