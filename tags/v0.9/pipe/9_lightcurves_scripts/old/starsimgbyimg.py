#
#	plot an image by image light curve of multiple images
#
#


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from pylab import * # matplotlib and NumPy etc
from variousfct import *


deckey = "dec1_lens_psf_full_10ih"
deckeyfilenum = "decfilenum_" + deckey
# we need this to select the right fields from the db


db = KirbyBase()
data = db.select(imgdb, [deckeyfilenum], ['>0'], returnType='dict', sortFields=['mjd'])
mjd = asarray(map(lambda x:float(x['mjd']), data)) - 54000
seeing = asarray(map(lambda x:float(x['seeing']), data))
count = asarray(range(len(data)))+1

deckey = "dec1_star15_psf_full_10ih"
intfieldname = "out_" + deckey + "_star15_int"
mag15 = -2.5 * log10(asarray(map(lambda x:float(x[intfieldname]), data)))

deckey = "dec1_star17_psf_full_10ih"
intfieldname = "out_" + deckey + "_star17_int"
mag17 = -2.5 * log10(asarray(map(lambda x:float(x[intfieldname]), data)))

deckey = "dec1_star13_psf_full_10ih"
intfieldname = "out_" + deckey + "_star13_int"
mag13 = -2.5 * log10(asarray(map(lambda x:float(x[intfieldname]), data)))

deckey = "dec1_star14_psf_full_10ih"
intfieldname = "out_" + deckey + "_star14_int"
mag14 = -2.5 * log10(asarray(map(lambda x:float(x[intfieldname]), data)))


err15 = mag15 - mean(mag15)
err17 = mag17 - mean(mag17)
err13 = mag13 - mean(mag13)
err14 = mag14 - mean(mag14)

prenorm = -2.5 * log10(asarray(map(lambda x:float(x['medcoeff']), data)))

renorm = map(mean, zip(err13, err14))

#plot(count, err15, '.', count, err17, '.',count, err13, '.',count, err14, '.', count, prenorm, '+', count, renorm, 'o')
#legend(('star 15', 'star 17', 'star 13', 'star 14', 'prenorm', 'renorm'))

plot(count, err15, '.', count, err17, '.',count, err13, '.',count, err14, '.')
legend(('star 15', 'star 17', 'star 13', 'star 14'))


grid(True)

#for i, image in enumerate(data):
	#text(count[i], prenorm[i], "%4.2f"%image['sigcoeff'], fontsize=9)
	#infv = min(err15[i], err17[i], err13[i], err14[i])
	#supv = max(err15[i], err17[i], err13[i], err14[i])
	#rrow(count[i], infv, 0, supv-infv)

	
# reverse y axis for magnitudes :
ax=gca()
ax.set_ylim(ax.get_ylim()[::-1])

xlabel('MJD [days]')
ylabel('Magnitude')


show()
#savefig(workdir + "lc.png")
#sys.exit()

# Add our renormalisation to the database !
renormfieldname = "renorm_2stars"
print "I will update this field :", renormfieldname
proquest(askquestions)

backupfile(imgdb, dbbudir, 'renorm')
if renormfieldname in db.getFieldNames(imgdb) :
	db.dropFields(imgdb, [renormfieldname])
db.addFields(imgdb, [renormfieldname + ':float'])

for i, image in enumerate(data):
	myrenorm = float(renorm[i])
	db.update(imgdb, ['recno'], [image['recno']], {renormfieldname: myrenorm})

db.pack(imgdb)


