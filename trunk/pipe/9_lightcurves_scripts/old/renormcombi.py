#
#	For a deconvolution, combines the light curves by night
#	To keep it simple, we call the same fct for each source
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from combibynight_fct import *
from variousfct import *
from pylab import * # matplotlib and NumPy etc

#deckey = "dec1_lens_psfnew56"


deckey = "dec1_lens_psf_full_10ih"
deckeyfilenum = "decfilenum_" + deckey
#
# we need this to select the right fields from the db


db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['>0'], returnType='dict', sortFields=['mjd'])
#images = db.select(imgdb, ['recno'], ['*'], returnType='dict')

groupedimages = groupbynights(images)
print "Number of nights :", len(groupedimages)

# Some control calculations
nightspans = map(nightspan, groupedimages)
print "Maximum night span :", max(nightspans), "hours."
nbimgpernight = map(len, groupedimages)
sumimgpernight = sum(nbimgpernight)
print "Number of images :", sumimgpernight

#deckey = "dec1_lens_psfnew56"

magas = mags(groupedimages, 'out_'+deckey+'_A'+'_int')
magbs = mags(groupedimages, 'out_'+deckey+'_B'+'_int')

rmagas = renormmags(groupedimages, 'out_'+deckey+'_A'+'_int', 'renorm_2stars')
rmagbs = renormmags(groupedimages, 'out_'+deckey+'_B'+'_int', 'renorm_2stars')


mjds = values(groupedimages, 'mjd')
seeings = values(groupedimages, 'seeing')
ams = values(groupedimages, 'airmass')
dates = asarray(mjds['median']) - 54000

#plot(mjds['median'], magas['median'], 'b.', mjds['median'], magbs['median'], 'r.')


#errorbar(dates, magas['median'], [magas['down'],magas['up']], fmt='.', color="#666666")
#errorbar(dates, magbs['median'], [magbs['down'],magbs['up']], fmt='.', color="#666666")

#errorbar(dates, rmagas['median'], [rmagas['down'],rmagas['up']], fmt='b.')
#errorbar(dates, rmagbs['median'], [rmagbs['down'],rmagbs['up']], fmt='r.')


#plot(dates, magas['median'], 'b.')
#plot(dates, magbs['median'], 'r.')

plot(dates, rmagas['median'], 'b+')
plot(dates, rmagbs['median'], 'r+')


#for i, n in enumerate(nbimgpernight):
	#text(dates[i], magas['median'][i], str(n), fontsize=12)
	#text(dates[i], magbs['median'][i], '%4.2f'%seeings['mean'][i], fontsize=8)
	#text(dates[i], magbs['median'][i]+0.05, '%4.2f'%ams['mean'][i], fontsize=8, color="#FF0000")

#allmaga = -2.5 * log10(asarray(map(lambda x:float(x['out_l10psf56A_int']), images)))
#allmjds = asarray(map(lambda x:float(x['mjd']), images))
#plot(allmjds, allmaga, 'g+')


# see all images, also the skipped ones :
allimages = db.select(imgdb, ['recno'], ['*'], returnType='dict', sortFields=['mjd'])
groupedallimages = groupbynights(allimages)
print "Number of nights :", len(groupedallimages)
allmjds = values(groupedallimages, 'mjd')
alldates = asarray(allmjds['median']) - 54000

for i, date in enumerate(alldates):
	axvline(date, ymin=0, ymax=0.1, color="#007700")	



grid(True)

#axis([300, 650, -10.2, -8.6])
# reverse y axis for magnitudes :
ax=gca()
ax.set_ylim(ax.get_ylim()[::-1])

title(deckey, fontsize=20)
xlabel('Time [days]')
ylabel('Magnitude')


show()
#savefig("oldpsf.png")

	
	
