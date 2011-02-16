#
#	Script to draw lightcurves mixed from different databases.
#



import os
import sys

pipedir = "/Users/mtewes/Desktop/sample_deconv/PIPE/"
sys.path.append(pipedir + "modules")

from kirbybase import KirbyBase, KBError
from combibynight_fct import *
from variousfct import *
from pylab import *



# Chandra
print "Chandra"

imgdb = "/Users/mtewes/Desktop/vieuxCombineTelescopes/J0806_chandra/database_tweaked.dat"
deckey = "dec1_lens_psf_full_10ih"
deckeyfilenum = "decfilenum_" + deckey
db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['>0'], returnType='dict', sortFields=['mjd'])

groupedimages = groupbynights(images)
print "Number of nights :", len(groupedimages)

# Some control calculations
nightspans = map(nightspan, groupedimages)
print "Maximum night span :", max(nightspans), "hours."
nbimgpernight = map(len, groupedimages)
sumimgpernight = sum(nbimgpernight)
print "Number of images :", sumimgpernight

chandra_i = images
chandra_gi = groupedimages
del chandra_gi[0]
del chandra_gi[20]


# Liverpool
print "Liverpool"

imgdb = "/Users/mtewes/Desktop/vieuxCombineTelescopes/J0806_liverpool/database.dat"
deckey = "dec5_lens_psfold468"
deckeyfilenum = "decfilenum_" + deckey
db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['>0'], returnType='dict', sortFields=['mjd'])

groupedimages = groupbynights(images)
print "Number of nights :", len(groupedimages)

# Some control calculations
nightspans = map(nightspan, groupedimages)
print "Maximum night span :", max(nightspans), "hours."
nbimgpernight = map(len, groupedimages)
sumimgpernight = sum(nbimgpernight)
print "Number of images :", sumimgpernight

lrt_i = images
lrt_gi = groupedimages

del lrt_gi[10]



lrt_mag17 = -2.5 * log10(asarray(map(lambda x:float(x['out_dec1_star17_psfold468_star17_int']), lrt_i)))
lrt_mean17 = mean(lrt_mag17)
chandra_mag17 = -2.5 * log10(asarray(map(lambda x:float(x['out_dec1_star17_psf_full_10ih_star17_int']), chandra_i)))
chandra_mean17 = mean(chandra_mag17)
lrt_add = chandra_mean17-lrt_mean17

chandra_magas = mags(chandra_gi, 'out_dec1_lens_psf_full_10ih'+'_A'+'_int')
chandra_magbs = mags(chandra_gi, 'out_dec1_lens_psf_full_10ih'+'_B'+'_int')
chandra_mjds = values(chandra_gi, 'mjd')
chandra_dates = asarray(chandra_mjds['median']) - 54000
chandra_seeings = values(chandra_gi, 'seeing')

lrt_rmagas = renormmags(lrt_gi, 'out_dec5_lens_psfold468'+'_A'+'_int', 'renorm4')
lrt_rmagbs = renormmags(lrt_gi, 'out_dec5_lens_psfold468'+'_B'+'_int', 'renorm4')
lrt_mjds = values(lrt_gi, 'mjd')
lrt_dates = asarray(lrt_mjds['median']) - 54000
lrt_seeings = values(lrt_gi, 'seeing')

figure(figsize=(5,8))


ax1 = axes([.12, .1, 0.8, 0.55])

errorbar(lrt_dates, asarray(lrt_rmagas['median']) + lrt_add + 12 +0.12, [lrt_rmagas['down'],lrt_rmagas['up']], fmt='.', color='#999999')
errorbar(lrt_dates, asarray(lrt_rmagbs['median']) + lrt_add + 12 -0.05, [lrt_rmagbs['down'],lrt_rmagbs['up']], fmt='.', color='#999999')

plot(lrt_dates, asarray(lrt_rmagas['median']) + lrt_add + 12 +0.12, 'b.', lrt_dates, asarray(lrt_rmagbs['median']) + lrt_add + 12 - 0.05, 'r.')
plot(chandra_dates, asarray(chandra_magas['median']) + 12, 'b+', chandra_dates, asarray(chandra_magbs['median']) + 12, 'r+')

#i = 20
#text(chandra_dates[i], chandra_magas['median'][i] + 12, str(chandra_gi[i][0]['imgname']))
#text(chandra_dates[i], chandra_magas['median'][i] + 12, 'o')



#errorbar(dates, rmagas['median'], [rmagas['down'],rmagas['up']], fmt='b.')
#errorbar(dates, rmagbs['median'], [rmagbs['down'],rmagbs['up']], fmt='r.')


grid(True)



#for i, image in enumerate(datalrt_dates):
#	#text(count[i], prenorm[i], "%4.2f"%image['sigcoeff'], fontsize=9)
#	infv = min(err17[i], err8[i], err15[i], err16[i])
#	supv = max(err17[i], err8[i], err15[i], err16[i])
#	arrow(count[i], infv, 0, supv-infv)


# reverse y axis for magnitudes :
ax=gca()
ax.set_ylim(ax.get_ylim()[::-1])


xlabel('Time [days]')
ylabel('Relative magnitude')




ax2 = axes([0.12, 0.68, 0.8, 0.2], axisbg='w', sharex=ax1)
setp(ax2.get_xticklabels(), visible=False)

#fig = gcf()
#fig.subtitle('J1406, Liverpool Telescope', fontsize=20)
figtext(0.12, 0.9, 'J0806+2006, Liverpool (.) & Chandra (+)', fontsize=14)

ylabel('Seeing ["]')
plot(lrt_dates, lrt_seeings['mean'], 'k.')
plot(chandra_dates, chandra_seeings['mean'], 'k+')
grid(True)


figtext(0.5, 0.6, 'A', fontsize=18, color='b')
figtext(0.5, 0.18, 'B', fontsize=18, color='r')



show()

