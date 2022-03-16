#
#
#	prepares HTML files
#	Only supports the new MCS PSF.
#
#	
#

execfile("../config.py")
import shutil
from kirbybase import KirbyBase, KBError
import variousfct
import star
import lookback_fct
import combibynight_fct

import numpy as np

from glob import glob
import ds9reg
import f2n

###### config ########


startat = 0
# you can put here an "iteration" number from which you want to restart, if you had to stop the scirpt etc.

redofromscratch = True

######################


lookbackkey = deckey	# This could be hardcoded to any other string.
lookbackdir = os.path.join(workdir, "lookback_" + deckey)

# Greeting ...
print "So you want to build lookback pages for", deckey, "?"

# We read in the point sources that should be available
ptsrc = [src.name for src in star.readmancat(ptsrccat)]
print "Sources : ", ptsrc

variousfct.proquest(askquestions)

if os.path.isdir(lookbackdir) and redofromscratch:
	print "The lookbackdir exists."
	print "I would delete existing stuff."
	variousfct.proquest(askquestions)
	shutil.rmtree(lookbackdir)

if not os.path.isdir(lookbackdir):
	os.mkdir(lookbackdir)


db = KirbyBase()

# We sort by setname, then by mhjd. So we will group sets together. Later code could rely on this sorting, so keep it like this please.
if thisisatest:
	print "This is a test run."
	images = db.select(imgdb, [deckeyfilenum, 'testlist'], ['\d\d*', True], returnType='dict', useRegExp=True, sortFields=['setname', 'mhjd'])
else:
	images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['setname', 'mhjd'])

print "I've will go for", len(images), "images, this is the last question."
variousfct.proquest(askquestions)

# We copy some files in our new lookbackdir :

shutil.copy("templates/indiv_page.css", lookbackdir)

# We read our big fat whole page template :

newpsfpagetemplatefile = open("templates/indiv_page_newpsf.html", "r")
newpsfpagetemplate = newpsfpagetemplatefile.read()
newpsfpagetemplatefile.close()

# We create a static link line to the first images of each set
setnames = sorted(list(set([image["setname"] for image in images])))
setnamelist = [image["setname"] for image in images]
setlinks = []
for setname in setnames:
	firstindex = setnamelist.index(setname)
	imgname = images[firstindex]["imgname"]
	setlinks.append('<a href="../%s/index.html">%s</a>'%(imgname, setname))
setlinkline = "&nbsp;" + " | ".join(setlinks)

# We measure the night limits :
nights = combibynight_fct.groupbynights(images, separatesetnames=True)
nightlengths = map(len, nights)
nightlims = np.add.accumulate(np.array(nightlengths)) + 0.5


# Before starting, we build an index.html in the lookbackdir, redirecting to the first image.
firstimglink = "%s/index.html" % (images[0]["imgname"])
indexhtml = """
<html>
<head>
<meta http-equiv="Refresh" content="0; URL=%s">
</head>
<body>
Your will be redirected <a href="%s">here</a>.
</body>
</html>
""" % (firstimglink, firstimglink)
indexfile = open(os.path.join(lookbackdir, "index.html"), "w")
indexfile.write(indexhtml)
indexfile.close()


for j, image in enumerate(images):
	
	if j < startat:
		continue
	
	print "- "*40
	print "%i / %i : [%s] %s"%(j+1, len(images), image[deckeyfilenum], image["imgname"])
	
	# The directory that will contain everything I will produce for this image :
	destdir = os.path.join(lookbackdir, image["imgname"])
	if not os.path.isdir(destdir):
		os.mkdir(destdir)
	
	# Hard-coding the navigation links :
	rightlinks = '<a href="../%s/index.html">[-200]</a><a href="../%s/index.html">[-50]</a><a href="../%s/index.html">[-20]</a><a href="../%s/index.html">[-5]</a><a href="../%s/index.html">[-1]</a>'% (images[(j-200) % (len(images))]["imgname"], images[(j-50) % (len(images))]["imgname"], images[(j-20) % (len(images))]["imgname"], images[(j-5) % (len(images))]["imgname"], images[(j-1) % (len(images))]["imgname"])
	leftlinks = '<a href="../%s/index.html">[+1]</a><a href="../%s/index.html">[+5]</a><a href="../%s/index.html">[+20]</a><a href="../%s/index.html">[+50]</a><a href="../%s/index.html">[+200]</a>'% (images[(j+1) % (len(images))]["imgname"], images[(j+5) % (len(images))]["imgname"], images[(j+20) % (len(images))]["imgname"], images[(j+50) % (len(images))]["imgname"], images[(j+200) % (len(images))]["imgname"])
	
	summaryline = "%04i/%04i : [%s]"%(j+1, len(images), image[deckeyfilenum])
	
	# Putting this first information into one dict that will be used to fill the template
	filldict = {"pagetitle":image["imgname"], "summaryline":summaryline, "rightlinks":rightlinks, "leftlinks":leftlinks, "setlinkline":setlinkline}
	
	##########################################
	# Preparing the html
	##########################################
	
	# Skim effect for the deconvolution
	
	# Deconvolution skim effect :
	width = 256
	height = 256
	pngimages = ["g.png", "resi.png"]
	npngimages = len(pngimages)
	
	decskim = ["""<img src='%s' width='%i' height='%i' usemap='#decskimmap' border='0' name='decskim' alt='' class="imgmargin">
	<map name="decskimmap">""" % (pngimages[0], width, height)]
	for i, pngimage in enumerate(pngimages):
		xmin = i * int(width/npngimages)
		ymin = 0
		xmax = (i+1)*int(width/npngimages)
		ymax = height
		decskim.append("""
		<area shape="rect" COORDS="%i,%i,%i,%i" href="" onClick="return false" onmouseover="decskim.src='%s';" alt="">
		""" % (xmin, ymin, xmax, ymax, pngimage))
	decskim.append("</map>")
	filldict["decskim"] = "".join(decskim)
	

	# Cosmics for the object
	usedobjkey = "obj_" + decobjname
	cosmicslistpath = os.path.join(workdir, usedobjkey, image['imgname'], "cosmicslist.pkl")
	if os.path.exists(cosmicslistpath):
		objcosmicslist = variousfct.readpickle(cosmicslistpath, verbose=False)
	else:
		objcosmicslist = []
		
	# To get the number of cosmics is easier ...
	objcosmicskey = usedobjkey + "_cosmics"
	nobjcosmics = image[objcosmicskey]
	
	
	# We do Similar things for the PSF :
	
	width = 256
	height = 256
	pngimages = ["s.png", "psfback.png"]
	npngimages = len(pngimages)
	
	psfskim = ["""<img src='%s' width='%i' height='%i' usemap='#psfskimmap' border='0' name='psfskim' alt='' class="imgmargin">
	<map name="psfskimmap">""" % (pngimages[0], width, height)]
	for i, pngimage in enumerate(pngimages):
		xmin = i * int(width/npngimages)
		ymin = 0
		xmax = (i+1)*int(width/npngimages)
		ymax = height
		psfskim.append("""
		<area shape="rect" COORDS="%i,%i,%i,%i" href="" onClick="return false" onmouseover="psfskim.src='%s';" alt="">
		""" % (xmin, ymin, xmax, ymax, pngimage))
	psfskim.append("</map>")
	filldict["psfskim"] = "".join(psfskim)
	

	# Cosmics for the PSF
	usedpsfkey = "psf_" + image[deckeypsfused]
	cosmicslistpath = os.path.join(workdir, usedpsfkey, image['imgname'], "cosmicslist.pkl")
	if os.path.exists(cosmicslistpath):
		psfcosmicslist = readpickle(cosmicslistpath, verbose=False)
	else:
		psfcosmicslist = []
		
	# To get the number of cosmics is easier ...
	#psfcosmicskey = usedpsfkey + "_cosmics"
	#npsfcosmics = image[psfcosmicskey]
	npsfcosmics = 0

	# And the masked regions :
	ds9regfilepath = os.path.join(configdir, usedpsfkey + "_mask.reg")
	psfmaskreg = ds9reg.regions(128, 128) # hardcoded for now ...
	if os.path.exists(ds9regfilepath):
		psfmaskreg.readds9(ds9regfilepath, verbose=False)

	##########################################	
	# PREPARING THE PLOTS
	##########################################

	
	lookback_fct.posplotbydate(images, image, deckey, ptsrc, os.path.join(destdir, "overview.png"), maglims = None)
	#posplotbyimg(images, nightlims, image, deckey, ptsrc, os.path.join(destdir,"zoom.png"), maglims = lookbackzoomgraphmaglims)
	lookback_fct.posplotbyimg(images, nightlims, image, deckey, ptsrc, os.path.join(destdir,"zoom_auto.png"), maglims = None)
	
	
	# Plot skim effect :
	width = 576
	height = 360
	#pngimages = ["zoom_auto.png", "zoom.png"]
	pngimages = ["zoom_auto.png"]
	npngimages = len(pngimages)
	
	plotskim = ["""<img src='%s' width='%i' height='%i' usemap='#plotskimmap' border='0' name='plotskim' alt='' class="imgmargin">
	<map name="plotskimmap">""" % (pngimages[0], width, height)]
	for i, pngimage in enumerate(pngimages):
		xmin = i * int(width/npngimages)
		ymin = 0
		xmax = (i+1)*int(width/npngimages)
		ymax = height
		plotskim.append("""
		<area shape="rect" COORDS="%i,%i,%i,%i" href="" onClick="return false" onmouseover="plotskim.src='%s';" alt="">
		""" % (xmin, ymin, xmax, ymax, pngimage))
	plotskim.append("</map>")
	filldict["zoomplot"] = "".join(plotskim)
	
	filldict["overviewplot"] = '<img src="overview.png" class="imgmargin">'
	
	
	##########################################
	# PREPARING THE FITS IMAGES
	##########################################
	
	# Deconvolution images :
	
	f2ng = f2n.fromfits(os.path.join(decdir, "g" +image[deckeyfilenum]+".fits"), verbose=False)
	f2ng.setzscale(-30.0 , "ex")
	f2ng.makepilimage(scale = "log", negative = False)
	f2ng.upsample(4)
	f2ng.drawstarlist(objcosmicslist)
	f2ng.writetitle("Object")
	f2ng.tonet(os.path.join(destdir, "g.png"))
	
	f2nresi = f2n.fromfits(os.path.join(decdir, "resi" +image[deckeyfilenum]+".fits"), verbose=False)
	f2nresi.setzscale(-30, +30)
	f2nresi.makepilimage(scale = "lin", negative = True)
	f2nresi.upsample(2)
	f2nresi.writetitle("Residues", colour=(255))
	f2nresi.tonet(os.path.join(destdir, "resi.png"))
	
	# the PSF
	
	psfdir = os.path.join(workdir, "psf_" + image[deckeypsfused], image['imgname'])
	
	f2nimg = f2n.fromfits(os.path.join(psfdir, "s001.fits"), verbose=False)
	f2nimg.setzscale("ex", 1.0e-3)
	f2nimg.makepilimage(scale = "log", negative = False)
	f2nimg.upsample(2)
	f2nimg.writetitle("PSF")
	f2nimg.tonet(os.path.join(destdir, "s.png"))
	
	f2npsfnum = f2n.fromfits(os.path.join(psfdir, "results/psf_num_1.fits"), verbose=False) # 128 128
	f2npsfnum.setzscale(-0.02, 0.02)
	f2npsfnum.makepilimage(scale = "lin", negative = False)
	f2npsfnum.upsample(2) # Now 256 x 256
	f2npsfnum.writetitle("Num part of PSF")
	f2npsfnum.tonet(os.path.join(destdir, "psfback.png"))
	
	
	"""
	f2ng001 = f2n.fromfits(os.path.join(psfdir, "g001.fits"), verbose=False) # 128 x 128
	f2ng001.setzscale(-20, 2000)
	f2ng001.makepilimage(scale = "log", negative = False)
	f2ng001.upsample(2) # Now 256 x 256
	for circle in psfmaskreg.circles:
		f2ng001.drawcircle(circle["x"], circle["y"], r = circle["r"], colour = (120))
	f2ng001.drawstarlist(psfcosmicslist)
	#f2ng001.writeinfo([image['imgname']], (255, 0, 0))
	f2ng001.writeinfo(["PSF stars"])
	f2ng001.tonet(os.path.join(destdir, "psfstars.png"))

	
	f2nresidu001 = f2n.fromfits(os.path.join(psfdir, "residu001.fits"), verbose=False) # 128 x 128
	f2nresidu001.setzscale(-3, 3)
	f2nresidu001.makepilimage(scale = "lin", negative = False)
	f2nresidu001.upsample(2) # Now 256 x 256
	f2nresidu001.writeinfo(["PSF residues"])
	f2nresidu001.tonet(os.path.join(destdir, "psfresi.png"))


	f2nfond001 = f2n.fromfits(os.path.join(psfdir, "fond001.fits"), verbose=False) # 256 x 256
	f2nfond001.irafcrop("[65:192,65:192]") # Now 128 x 128
	f2nfond001.setzscale(-1.0e-3, 1.0e-3)
	f2nfond001.makepilimage(scale = "lin", negative = False)
	f2nfond001.upsample(2) # Now 256 x 256
	f2nfond001.writeinfo(["PSF background", "(zoom on center)"])
	f2nfond001.tonet(os.path.join(destdir, "psfback.png"))

	"""
	
#	preparing the bla bla to write into the html page	
	
	description = []
	description.append("%s UTC" % image["datet"])
	description.append("Seeing [arcsec] : %4.2f, ellipticity : %4.2f" % (image["seeing"], image["ell"]))
	description.append("Airmass : %4.2f, azimuth : %4.1f" % (image["airmass"], image["az"]))
	description.append("")
	description.append("medcoeff : %5.2f (span : %5.2f), decnorm : %5.2f" % (image["medcoeff"], image["spancoeff"], image[deckeynormused]))
	description.append("")
	description.append("Sun altitude [deg] : %+4.1f / sep [deg] : %4.1f" % (image["sunalt"], image["sundist"]))
	description.append("Moon ill [%%] : %3.f / sep [deg] : %4.1f" % (image["moonpercent"], image["moondist"]))
	description.append("Sky level [e-] : %6.1f" % image["skylevel"])
	description.append("Preali/Postali stddev [e-] : %4.1f / %4.1f" % (image["prealistddev"], image["stddev"]))
	
	#description.append("astrocomment : %s" % image["astrocomment"])
	description.append("Alignment comments : %s" % image["alicomment"])
	description.append("PSF used : %s" % image[deckeypsfused])
	description.append("")
	#description.append("%i cosmic pixels on object" % nobjcosmics)
	#description.append("%i cosmic pixels on PSF" % npsfcosmics)
	#description.append("")
	description.append("Prereduction comment 1 : %s" % image["preredcomment1"])
	description.append("Prereduction comment 2 : %s" % image["preredcomment2"])
	description.append("Prereduction float 1   : %f" % image["preredfloat1"])
	description.append("Prereduction float 2   : %f" % image["preredfloat2"])
	
	filldict["description"] = "\n".join(description)
	
	
	filledhtml = newpsfpagetemplate % filldict # You love python, don't you ?
	
	
	# We write the filled template into an index.html file
	htmlpage = open(os.path.join(destdir, "index.html"), "w")
	htmlpage.write(filledhtml)
	htmlpage.close()

	
	if j == 0:
		print "First image done :"
		print os.path.join(lookbackdir, image["imgname"], "index.html")
		variousfct.proquest(askquestions)


print "- "*40
variousfct.notify(computer, withsound, "Lookback page building done.")
print "You can visit the results here :"
print os.path.join(lookbackdir, "index.html")





"""
		psfdir = workdir + "psf_" + image[deckeypsfused] + "/" + image['imgname'] + "/"
		
		f2npsfr = f2n.fromfits(psfdir + "psfr.fits", verbose=False)
		f2npsfr.setzscale(-0.1, 0.1)
		f2npsfr.makepilimage(scale = "lin", negative = False)
		f2npsfr.upsample(2)
		f2npsfr.writetitle("psfr")
		f2npsfr.tonet(destdir + "psfr.png")
		
		f2ns001 = f2n.fromfits(psfdir + "s001.fits", verbose=False)
		f2ns001.setzscale(1e-7, 0.004)
		f2ns001.makepilimage(scale = "log", negative = False)
		f2ns001.upsample(2)
		f2ns001.writetitle("s")
		f2ns001.tonet(destdir + "s.png")


		
		psfstarimglist = glob(psfdir + "psf??.fits")
		nbrpsf = len(psfstarimglist)
		
		composelist = []
		for j in range(nbrpsf):
		
			inputfitspath = psfdir + "psf%02i.fits"%(j+1)
		
			f2nimg = f2n.fromfits(inputfitspath, verbose=False)
			f2nimg.setzscale(0, 1)
			f2nimg.makepilimage(scale = "lin", negative = False)
			f2nimg.upsample(2) # 128 x 128
			#f2nimg.writeinfo([image['imgname']], (255, 0, 0))
			#f2nimg.writeinfo(["","g001.fits"])
			f2nimg.writeinfo("%i" % (j+1))
			composelist.append(f2nimg)
	
		# We fill with blanks and cut at 4 images :
		blank = f2n.f2nimage(shape = (128,128), fill = 0.0, verbose=False)
		blank.setzscale(0.0, 1.0)
		blank.makepilimage(scale = "lin", negative = False)
		composelist.extend([blank, blank, blank])
		composelist = composelist[:4]
		#print composelist
		composelist = [ [ composelist[0], composelist[1] ], [ composelist[2], composelist[3] ] ]
		f2n.compose(composelist, destdir + "psf_comp.png")	
	
	
	
"""
	
