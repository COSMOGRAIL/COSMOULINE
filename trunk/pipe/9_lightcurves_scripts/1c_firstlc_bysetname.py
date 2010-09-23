#
#	For a deconvolution, combines the light curves by night to make a first plot.
#	This script shows the points of 1 deconvolution only, possibly with multiple sources.
#	Colouring is done according to setnames.
#	IT RELIES ON THE DECONVOLUTION INFORMATION GIVEN IN SETTINGS.PY !
#	
#	You will typically want to make custom plots for your lens later
#	This is just to give a first automatic view, without any configuration,
#	using the current settings of settings.py with which you did the deconvolution.
#
#	


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from combibynight_fct import *
from star import *


from numpy import *
import matplotlib.pyplot as plt


print "You want to analyze the deconvolution %s" %deckey
print "Deconvolved object :", decobjname

# we read params of point sources
ptsrc = readmancatasstars(ptsrccat)
nbptsrc = len(ptsrc)
print "Number of point sources :", nbptsrc
print "Names of sources : "
for src in ptsrc: print src.name

#proquest(askquestions)


db = KirbyBase()

# the \d\d* is a trick to select both 0000-like and 000-like
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True)


# We see which setnames are involved and rearrange our data
setlist = []
setnames = list(set([image["setname"] for image in images]))
for setname in setnames :
	setimages = [image for image in images if image["setname"] == setname]
	setlist.append({"setname":setname, "n":len(setimages), "setimages":setimages})	


plt.figure(figsize=(12,8))	# sets figure size

for imgset in setlist:
	print imgset["setname"], imgset["n"]
	
	#if imgset["setname"] != "Mer1" or imgset["setname"] != "Mer2" :
	#	continue
	
	groupedimages = groupbynights(imgset["setimages"])
	print "Number of nights :", len(groupedimages)

	# Now we put together the different sources in unique arrays, so that we get only one colour per setname :
	srcmaglist = []
	srcmaguplist = []
	srcmagdownlist = []
	srcdatelist = []
	for src in ptsrc:
		mymags = asarray(mags(groupedimages, 'out_'+deckey+'_'+ src.name +'_int')['median'])
		mymagups = asarray(mags(groupedimages, 'out_'+deckey+'_'+ src.name +'_int')['up'])
		mymagdowns = asarray(mags(groupedimages, 'out_'+deckey+'_'+ src.name +'_int')['down'])
		mhjds = asarray(values(groupedimages, 'mhjd')['median'])
		dates = mhjds - 54000
		
		srcmaglist.append(mymags)
		srcmaguplist.append(mymagups)
		srcmagdownlist.append(mymagdowns)
		srcdatelist.append(dates)
	
	allmags = concatenate(srcmaglist)
	allmagups = concatenate(srcmaguplist)
	allmagdowns = concatenate(srcmagdownlist)
	alldates = concatenate(srcdatelist)

	
	#seeings = values(groupedimages, 'seeing')
	#ams = values(groupedimages, 'airmass')
	
	
	plt.errorbar(alldates, allmags, [allmagdowns,allmagups], linestyle="None", marker=".", label = imgset["setname"])
	#plt.plot(alldates, allmags, linestyle="None", marker=".", label = imgset["setname"])


plt.grid(True)

# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

plt.title(deckey, fontsize=20)
plt.xlabel('Time [days]')
plt.ylabel('Magnitude')

plt.legend()
plt.show()

	
