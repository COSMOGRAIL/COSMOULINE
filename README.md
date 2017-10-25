# COSMOULINE

COSMOULINE is a python/IRAF/MCS ensemble of scrips designed to reduce images taken within the COSMOGRAIL collaboration into nice light curves. It is developed within the [COSMOGRAIL](http://www.cosmograil.org) collaboration. It is a bit of a mess, but hey, at least it's public !

In case of any questions, feel free to open an issue here on GitHub.


## License

If you use this code, please cite the [COSMOGRAIL](http://www.cosmograil.org) collaboration.

If you make use of the PyMCS PSF fitting and/or two-channel deconvolution scheme, please cite the corresponding publications ([Magain+1998](http://adsabs.harvard.edu/abs/1998ApJ...494..472M), [Cantale+2016](http://adsabs.harvard.edu/abs/2016A%26A...589A..81C))

Copyright (©) 2008-2017 EPFL (Ecole Polytechnique Fédérale de Lausanne)
Laboratory of Astrophysics (LASTRO)

COSMOULINE is free software ; you can redistribute it and/or modify it under the terms of the 
GNU General Public License as published by the Free Software Foundation ; either version 3 
of the License, or (at your option) any later version.

COSMOULINE is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY ; without 
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
General Public License for more details (LICENSE.txt).

You should have received a copy of the GNU General Public License along with COSMOULINE ; if not, 
write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.

## Contents

- pipe, lcmanip and sampleconfig folders : collection of scripts used to reduce the images
- cosmouline.png: visual representation of the data reduction pipeline
- doc folder: tex code for a handbook written by the first authors of COSMOULINE. Complementary to this README
- skymaker : few scripts to build simulated images
- README.md (this file): provides a bunch of useful information about the software, including a step-by-step guide
- LICENSE.txt :




# How to use the COSMOULINE Pipeline

advices and stuff (VB, 06/2015)



##	GENERAL INFORMATIONS


COSMOULINE goal is to reduce the already flatfielded and debiased images, in order to measure the luminosity variation of the lens images over time. In short, it substracts the sky, aligns and normalises the images, determines a PSF fit from chosen stars, extracts the lens and some stars from the image, deconvolves them, measures their luminosity and writes everything in a nice, light database.


COSMOULINE pipeline map (pardon my drawing skills). Also have a look at cosmouline.png


			        __config.py
			       /
		              /
	        ____pipe_svn--		
	       /	      \
	      /		       \__scripts repository (0-9 + extrascripts)
	     /
	    /
	   /			    __ali (aligned images)	
	  /			   /
     | COSMOULINE--data--(one per lens)-- plots (all kind of pdf images)
	 |\			  \ 
	 | \			   \__*database, *reports, *png folders (*will be created during the reduction)... 
	 |  \
	 |   \							 	
	 |    \							  __settings.py (the one we tweak)
	 |     \						 /
	 |      \____configs--(one per lens copied from sample)---
	 |     						         \__ .cat and .txt files, used by scripts
	 | 
	 | 
	 | 
	 \  			  __ samplelcmanip.py / sampleconfig.py
	  \			 /				
	   \			/
	    \____lcmanip_svn-------- scripts and stuff
	    
	     		       				
	       
The 'pipe_svn' directory (hereafter pipedir) contains all the scripts needed for the reduction process. You do not need to change anything into the pipedir, except if you want to change deeply the code or the files organisation. One exception though, in 'config.py', the configdir path is related to the lens you are currently working on.

The configs directory, containing one directory per lens (hereafter configdir) is where your configuration scripts are. Also, it contains settings.py, which regroups all the parameters you will tweak when playing with the pipeline.

The data directory, containing one directory per lens (hereafter datadir) is where the data are written. the scripts in the pipedir typically write all their outputs in there.

The lcmanip_svn directory (hereafter lcmanipdir) is where you will cook your .rdb file, before feeding PyCS with it. But you have a long way ahead before reaching this part...

	       
	     

##	RUN PREPARATION


For every new lens, make a related directory into configs and data. There is a 'sampleconfig_svn' directory into 'configs', copy it with the name your lens (e.g. WFI2033_ECAM, it will be your new configdir). In data, simply create a new empty directory (e.g. WFI2033_ECAM, it will be your new datadir)

The scripts in the pipedir will write in the corresponding datadir, and the parameters of your reduction are to be modified in the corresponding configdir, into 'settings.py'

In config.py in your pipedir, set a proper path to your corresponding configdir.
In the settings.py in your configdir, set "workdir" to the corresponding datadir.


You execute your scripts in pipedir, which is provided with a link to your configdir, which is itself linked to your datadir:

pipedir --> configdir --> datadir


Keep the settings.py from your configdir open, all the modification will be done in that file. Then, move to your pipedir. Now, you should be more or less ready, let's rock.



###	0_preparation_scripts


Scripts to crop images (remove ugly borders). Need to be adapted for every set of files, hardcoded.




###	1_character_scripts


Here, we import the data of prereduced images and create a new database of prereduced images.

1a :  In the importation paragraph of settings.py, give a path, setname and telescopename to the prereduced set you will import. Then, execute 1a.(One set after the other). The database is created in your datadir, as database.dat (hereafter db).

1b :  To be used right after 1a. It convert the pixels counts of the images into electrons counts, copy the images in your datadir, in ali/, and empty their headers. This does not affect the db (as every scripts labellised with _NU, for No Update).

2a : add some astronomical stuff to the db, such hjd of observation, sun position, moon distance... it uses the ephem python module. In settings.py, in astrocalc paragraph, be sure to select the right xephemlens line !

   ----- WARNING, on regor2, you must import python/2.6.6 to use that module, but no scisoft modules should be imported, or you will have a python version conflict error... -----
   
3a : run sextractor on the images, with default_see_template.sex as parameterfile (It should be fine as it is for ECAM images). For each images in ali, it creates a .cat file containing the extracted objects from the images.

   ----- WARNING, on regor2 remove your python/2.6.6 module AND your scisoft modules - do not forget to add them again after -----  

3b : update the db with informations (seeing and ellipticity, median values) from the .cat files.

4a : update the db with other informations (skylevel and stddev of the sky), computed from fits images with pyfits


other files


1c, 2b, 3c, 4b : write reports of the previous operation in your datadir. Basically, it displays what had been added to the db in the previous steps

default.*      : default parameters used by sextractor. Pretty fine as they are for ECAM images. All the witchcraft related to the stars exctraction is in them, so treat with care...

fac_make_pngs  : make (big) pngs of the images (in ali) and wrap them in a nice tarball (in case you have way too much space and want to fill it with workstuff)





###	2_skysub_scripts


1 : substract the sky from the images. Practically, it extracts an image of the sky for each original image, substract the sky to the original image, and save both of them (sky and skysubstracted) in ali (in your datadir).

2 : build pngs of the skysubstracted and sky images, along with a random bunch of sextracted stars on them (thanks to the alipy module). You can find them in your datadir, on sky_png. Have a look at them (a tarball is built if the flag makejpgarchives in settings.py is set on True), you can make a first remove of the crappy images -or let the pipeline do it by itself later on...-

3 : (facultative, but recommended !) remove the original electron images, as we do not need them anymore (at this point, we have the skysubstracted images AND the corresponding sky)


other files


1_alt_noskysub : mimic the sky substraction on simulated images, just that the pipeline won't complain later...

1_alt_skysub   : do the skysubstration, but with a flat value for the sky (useful for simulated images) 

default.*      : default parameters used by sextractor. retty fine as they are for ECAM images. All the black magic related to sky construction and substraction is in them, so modify with huge caution...





###	3_align_scripts


1a  : now, we will align the images. This is done by selecting some stars on a reference image. Thus, we need a reference image, and its 'best' stars.
To find a reference image (hereafter refimg), we can look at the report files from 1_character_scripts. In your datadir, use the report_seeing to select an image with a high number of goodstars and small seeing, and put it as refimgname in the alignment section of your settings.py. Then, open alistars.cat in your configdir (or create it) and add some reference stars coordinates from that refimg with, e.g., ds9. Put the approximate coordinates and flux of a high number of stars, e.g. 30. Once this is done, DO NOT FORGET to add more infos in your setting.py : the lens region coordinates, the empty region coordinates. Put the dimensions of the aligned images at 4000*4000 for ECAM. Aaaaaand eventually launch the script ! You may check the output png to see if everything went correctly.

1b  : Now that we have the coordinates of reference stars on our refimg, we can try to align the other images on it. This script only find the matching reference stars on the other images, and deduce the shift and rotation to make to align each image with the refimg. It DOES NOT align them, though, but add a flag (flagali) to the db, and set it to False if some image cannot be aligned.

2a  : This will align the images to the refimg. Launch it on multiple procs to gain some time (on regor2, type srunx to allow yourself a node to compute on, and then type nice +19 python 2a_multicpu... - this set the python task priority to low, avoiding slowing the node)

3   : Set the gogogo flag to False if the flagali flag is False. Thus, these images won't be considered anymore.

4   : Generates pngs from the aligned fits files. Have a look at them, and if something goes wrong add the image to the skiplist.

other files


0_alt_no_ali  : if you do not want to align your images but do a pseudoalignment instead...

1c, 2b	      : write reports of the previous operations in your datadir

5	      : remove non aligned images, as we do not need them anymore. Facultative, but save some disk space.




###	4_norm_scripts


1a  : compute some statistics on the empty region which should have been defined before launching 1a in 3_align_scripts, and add them to the database. 
Take the time right now to fill in the normstars.cat file in your configdir. These stars can be the same that the one selected for alignment, so you can basically copy your alistars.cat 
in your normstars.cat. These stars will be used to prenormalize the images.


1b  : add some noise when columns or row have a 0 value in our images. This may help the next scripts, as sextractor is not fond of 0...

1c  : compute the mean value in the emptysky region and add it to the whole image. It corrects the sky substration from sextractor that is usually a bit too efficient. 
The efficiency of this step is yet to be tested...

2a  : run sextractor on the aligned images, and write the aperture photometry (by default for 30, 90 and 'auto' radius in pixels) in an .alicat file in your alidir. 
This will be used as a normalisation coefficient later on. Note that this is done on all the sextracted objects of your images.

2b  : facultative (but needed for plot), write these apertures photometry in the db. To do so (and to execute the following facult. scripts as well), you need to define on which stars you want to perform the computations. These stars are to be written in photomstars.cat in your configdir, and can once again be the same that in alistars.cat and normstars.cat

2c  : facultative, write an estimation of the peak values (with the skylevel) of each stars of photomstars.cat in the db.

2d  : facultative, plot the peak values histogram for each star. It may help to select some good stars for the PSF later, so have a look at the plots...

3a  : take all the normstars and their aperture photometry in the database, and compute a first guess normalisation coefficient with it related to the reference image. 
As normalisation coefficient we take the median value (we call it medcoeff) of the ratios between normstars of the images (one after the other) and the normstars of the refimg.

3c  : plot the aperture photometry of each the stars (for all images), with each aperture, and also show the medcoeff computed above. Assuming the medcoeff should not vary too much, 
it gives you an idea on the quality of your dataset so far.


5   : make histograms with some statistics of ours plots (ellipticity, seeing, medcoeff and skylevel). It gives also a good idea of the quality of our datasets, 
but we can disregard the bad images later on...  



other files


3b  : write reports of the previous operations in your datadir.


4a  : prepare images to combine in order to obtain a good deep field image by stacking images. Run 5_histo_multifield before, and have a look at the histograms produced. It will help you select a set of parameters to enter in the Deep Field Combination paragraph of your settings.py. By adding these parameters, we select only a certain number of images to create our deep field image. The present script prepare the images, by normalising them and putting them in a new directory. This step takes really long, but is optional and we can go on with further scripts without any conflicts.

4b  : next step of the previous script : combine the images into one single deep field image. May crash if you use too much images (thks to Iraf)

4c  : draw circles around the alistars on the deep field image, to have it nicer as ever ! 

default.*      : default parameters used by sextractor. Fine as they are for ECAM images (I hope so). All the dark arts related to aperture photometry is in them, so modify with tremendous attention...




###	5_pymcs_psf_scripts


1  : Ok, now the fun begins. You need to select a certain number of stars to build the PSF for each images. You then need to create a .cat file with these stars. 
In your configdir, create a 'psf_mypsfname.cat' with the stars you want to use for your PSF construction (same format as alistars, normstars,...) 
In settings.py, under the PSF Construction paragraph, set your psfname as 'mypsfname'. The present script will create a new psfdir in your datadir, with a lot of stuff on it. 
A good idea may be to select some images to put in your testlist (with the refimg among them), to build different PSF sets (i.e. using different stars), then to choose the best set 
of stars for PSF construction and finally to compute the PSF on all images. You can perform the steps from 1 to 5 with test images (it is quite fast for only 10 images), and then select 
the best PSF set according to whatever criterias you like.
Protip : to build your testlist, you can use report_seeing in your datadir. Do not forget to launch reset_testlist.py and set_testlist.py in extrascripts 

2a  : This script will extract the psf stars for each image, and save them in the corresponding psfdir in your datadir. Also, it gives you instructions to build masks for your psfstars. Look just below to know more about it.-----WARNING : on regor2, remove the modules python 2.6.6 and scisoft/iraf or it will crash -----

2b  : facultative (but recommended). The stars you selected for the psf construction may have a companion star nearby, or be polluted by god knows what. In order to avoid it polluting our psf construction, we can build some masks for our stars. Thus, go into your datadir/psfdir/imgrefdir/results. With ds9, you can plot the so-called star_00*.fits, which are images of your psf stars. Inspect them: if one of it is polluted, select the polluted region and save it (region->save region) under your configdir/mypsfname_mask_#.reg, but WARNING, here the # is not the number of the star, but the name you gave it... for example, if you mask star_002.fits, the mask should be saved as mypsfname_mask_b.reg . Anyway, the script 2a gives you the correct paths to use. However, do not mask cosmics, the following script will do it for you

3  : facultative (but recommended). Find automatically cosmic rays on your images and mask them. 

4  : We finally build the PSF for the selected cleaned stars, by fitting a moffat with some wavelets on it. It takes some time, though. In your psfdir, for each image, the results directory contain some interesting stuff on it. If some images are troublesome, the script automatically put them into a kicklist. However, it may be a good idea to look at the resulting images (using the next script) the kick bad images by hand. Note that this script may take quite long if your run on only 1 core, so, on regor2, allow yourself a nice node to work in (type ''which srunx'', then change -n (or -c ) for the desired number of cores).

5  : Build overview images of the psf construction process in your datadir, under mypsfname_png. Look at them, to check that everything went as you wish. As said above, if you observ that some images are troublesome, put them in the corresponding psfkicklist (they will be kicked for the deconvolution with the corresponding psf set, that's why we don't put them in the general kicklist)


 
COMMENTS 

Knowing which PSF set is the best (or even if a psf set is good enough to be used) is not that simple. There is however a few tricks that may help : 

-select enough psf stars per set, let's say 6. No need to take the brightest ones though, but avoid the ones that are too faint. 
Use the result from 4c in 4_norm_scripts to select your psfstars. Also look at the alistars.png. Avoid the stars that fall on the dead pixels columns as well.
	
-have a look at your numerical psf plot. Also, by looking at your total psf plot, you will see immediately is something went really wrong. 
	
	

Finally, as computing the psf does not modify the db, you can already go on with the extraction part below, which is completely decorrelated from psf construction



###	6_extract_scripts


12  : This script will extract some small stamps around the object you selected (typically, your psf stars and your lens), mask cosmics and replace NaN values. This will be used for your deconvolution later on. In order to do this, in settings, give the name of the object you want to extract (a,b,c,lens,...), and in your configdir create an obj_name.cat where you will put the coordinate of that object (still the same coordinates than in your alistats.cat...). For your lens coordinates, you can take the center of the region defined in the alignment section of your settings.py (if you did it well back then, but you did, didn't you ?)

12_all : Same as 12 above, but lauch a serial extraction of a whole list of objects. Do not forget to create the obj_name.cat files. Use the objlists field in settings. This is particularly useful if parallell extractions are too slow, for example if the writing disk accesses are slow.

3  : makes pngs of the extracted object, with their mask. Useful if you want to check if an object is too often polluted, but you should already have seen it before when checking your psf...just saying...



other files


1a, 1b, 2 : old scripts, now combined altogether in 12




###	7_deconv_scripts / 8_renorm_scripts


Okay, now the structure of the pipeline is getting a bit peculiar...Let's start by giving the general idea:

We want to deconvolve the lens, using a given psfset, but first, we need to normalise properly the images. Our normalisation coefficient computed before is not precise enough, so we need to find a better coefficient. In order to do this, we can use the information contained in the stars. Indeed, we know that the stars are in fact point sources, so we can apply the deconvolution on the stars and use the resulting flux to normalise better our images. Thus, we first perform the deconvolution on the stars normalised with our previous medcoeff, then compute a new normalisation coefficient, renormalise the images with that new coefficient and finally deconvolve the lens itself. Of course, the images here are in fact the small stamps extracted in the previous script folder (6_extract_scripts)

Practically, it works as follows : 


7/0  : you can edit that script and configure it to generate a skiplist according to some criterias (seeing, ellipticipy, medcoeff...). You will have to copy that list into a corresponding skiplist in your configdir (the script will give you the path). Do it for E.V.E.R.Y. object you will deconvolve. The object selection is done in your settings.py, in the deconvolution section. Set the 4 dec*name with care and with respect to what you are currently doing. Everytime you switch between objects or between testset or fullset of images, you should tell it to your settings.

7/1  : prepare a specific decfolder in your datadir for the images you will deconvolve. It select only the images that are not in your psfskiplist from 5_, and that are not in your decskiplist prepared in the previous script. 

7/2  : apply the normalisation coefficient on the images in the specific decfolder prepared in 7/1. 

7/3  : before launching it, you must create a .cat file in the configdir with the coordinates of the object you want to deconvolve. But this time, the coordinates are the physical ones from the stamps images. Practically, the coordinates will be 33,33 (as the stamp size is hardcoded somewhere in the config.py file...) but if you're not sure then it is worth checking the fits images in your datadir. Then, the script will copy the template_in.txt and template_extract.txt of your configdir into your decdir, as the input parameters for the deconvolution. The idea here is to tweak the template files and launch 7/3+7/4 if you want to test different parameters for your deconvolution.

7/4  : critical script here, we finally deconvolve our images. As said before, if you want to change your deconvolution parameters tweak the template_in.txt file in your configdir and relaunch 7/3 before 7/4. Depending on the obscure parameters you will chose in your template_in.txt, running this script may take some time.

7/5a  : that script makes overview png of the deconvolution process in your datadir. It starts with the reference image, and then go one with the other images. You can check first the reference image to have a guess if the deconvolution went well.

7/5b  : show you more precisely the astrometry of your object (the thing you put at 33,33 above). Modify your corresponding .cat file then, and use it as a reference for the following scripts.

7/6  : write the results (the flux of the deconvolved images?) into the database, mandatory for the 8/ scripts. 

--Perform ALL these steps with every stars you will use to compute your new normalisation coefficient. First on a bunch of test images (thus obtaining the precise astrometry), and then on all the images. Once this is done, go to 8/:

8/1a  : now you can compute the renormalisation coefficient. Choose the stars which were well deconvolved, and put their corresponding decdir into the renormsources. Then choose the renormname according to it. This script will make a plot of your new medcoeff over time, that you can look at to check that things went in overall well.

8/2  : plot the new medcoeff for every images according to which stars you used. Useful for checks.

Now, change the decnormfieldname in your settings.py to your new normalisation coefficient name, and go on with the lens deconvolution, following the steps from 7/0 to 7/6, as for the stars deconvolution. The trickiest part here is clearly 7/3-7/4, where you will have to change the obscure coefficients of the template_in.txt file in your configdir, deconvolve the images, and start again (and again and again and again...sigh) if you are not happy with it. Start with a bunch of test images before going on the full set ! And good luck...


Things to check if you want to make a good deconvolution:
	Your overall background should be quite small, if possible not negative (even if having a minlevel of -1 is OK, I guess)
	The contrast in your background should not be too steep or too flat, and you shouldn't have more peak regions than deconvolved object (it makes sense, I guess...)


other files


7/7 , 7/8: plot some stuff related to the deconvolution to check everything went well. Does not work everytime... 

8/old_1a : old normalisation script, not used anymore.

8/1b     : write report of the new normalisation coefficient.

8/3fac   : same as 8/2, but for other objects than the stars used for renormalisation (does not seem to work, though. Look at the deckey...?)





###	8_pyMCS_lookback_scripts



1  : this script will build html pages which give you an overview of your deconvolution process.


other files


template   : config file for 1


###	9_quicklook_lc_scripts


No need for script by script description here, they are named straightforwardly. Basically, they plot a lightcurve, mag vs jds, and add a colorbar related to different observables (skylevel, ellipticity,...). One exception though, for the 1_by_night, which merge the points from the same night.

run "csh plotall.csh" to launch them altogether.



###	9_export_scripts


export : simply export your database into your configdir. It creates a date_lens_db.dat, date_lens_db.pkl and date_lens_readme.txt that you will use later on.



###            lcmanip


Now that you have exported your db, you can start to prepare your lightcurves for further PyCS treatment.

Start by making a copy of sampleconfig.py as config.py (in the lcmanip dir !!). In it, give the path to lcmanipdir and lcmanipfile. This two fields are related to where you will make a copy of samplelcmanip.py. As your export script has created the .pkl and .dat files into your configdir, a good idea is to copy samplelcmanip.py in your configdir as well, under date_lens_lcmanip.py (for name consistency). Thus, the path to lcmanipdir will be your configdir, and lcmanipfile will be date_lens_lcmanip.py 

Go back to your configdir and edit your lcmanip file. In there give the path to your dbfilename (the pkl file created by the export script), and which deconvolution you want to use (as you may have performed several of them). Keep it open before executing the following scripts:

In lcmanipdir:

addfluxes  : use it if you want to merge two sources in your image into a single flux.(not sure of that, however)

join       : merge the points from one same night into a single point, and give it some errorbars. In your lcmanipfile, add the name of the sources you will import (typically A, B, ...), the normalisation coefficient to use, which set of data and telescopenames you wish to merge. You can select which criterias you will apply to disregard or not some images. You can also create a skiplist of your own if you want to disregard any images for personnal reasons. This script will create some plots, which show the lightcurves and the evolution of the magnitude error. And above all, it will create a nice database (the .rdb file) that you can use directly with PyCS, and then show it to the world ! But this is another topic... :-)



###  ---The END--- 

(clap clap clap!)

