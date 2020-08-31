execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import glob
import astropy.io.fits as pf
import numpy as np
import matplotlib.pyplot as plt


def replacezeroes(filename, value):
    myfile = pf.open(filename, mode='update')
    scidata = myfile[0].data
    for x in range(len(scidata)):
        for y in range(len(scidata[0])):
            if scidata[x][y] < 1.0e-8:
                print "Nearly zero at ", x, y
                scidata[x][y] = value
    myfile.flush()


def replaceNaN(filename, value):
	sigstars = pf.open(filename, mode='update')
	scidata = sigstars[0].data
	if True in isNaN(scidata):
		print "Yep, some work for me : ", len(scidata[isNaN(scidata)]), "pixels."
	scidata[isNaN(scidata)] = value
	sigstars.flush()

def isNaN(x):
	return x!=x

object = 'RXJ1131-1231'
dir = ['15-04-2018', '16-04-2018','17-04-2018','18-04-2018', '21-04-2018']
dark_directory = 'Darks_22-04-2018'
reduced_dir = rawdir + '/reduced/'
if not os.path.exists(reduced_dir):
    os.mkdir(reduced_dir)



files_dark = glob.glob(os.path.join(rawdir, dark_directory) + '/Dark-*.fts')
data_size = np.shape(pf.open(files_dark[0])[0].data)
masterdark = np.zeros(data_size)
dark_count = 0.
for f in files_dark :
    header = pf.open(f)[0].header
    if header['EXPTIME']==300. :
        dark_count +=1.
        masterdark += pf.open(f)[0].data

masterdark = masterdark / dark_count
print "I have %i darks in %s with an exposure time of 300s."%(dark_count, dark_directory)


for d in dir :
    path = os.path.join(rawdir, d)
    print "I'm in : ", path

    files_bias = glob.glob(path + '/Bias-*.fts')
    files_flat = glob.glob(path + '/AutoFlat-*.fts')
    files_science = glob.glob(path + '/' + object + '*.fts')

    dark_count = 0.
    bias_count = 0.
    flat_count = 0.
    science_count = 0.

    masterbias = np.zeros(data_size)
    masterflat = np.zeros(data_size)

    for f in files_bias:
        bias_count +=1.
        masterbias += pf.open(f)[0].data

    for f in files_flat :
        flat_count +=1.
        masterflat += pf.open(f)[0].data


    masterbias = masterbias / bias_count
    masterflat = masterflat / flat_count
    masterflat = (masterflat - masterdark) / np.median(masterflat - masterdark)

    print "I have %i flats in %s"%(flat_count, d)
    print "I have %i bias in %s"%(bias_count, d)

    hdu1 = pf.PrimaryHDU(masterdark)
    lists = pf.HDUList([hdu1])
    lists.writeto(path + '/masterdark.fits', clobber=True)

    hdu2 = pf.PrimaryHDU(masterbias)
    lists = pf.HDUList([hdu2])
    lists.writeto(path + '/masterbias.fits', clobber=True)

    hdu3 = pf.PrimaryHDU(masterflat)
    lists = pf.HDUList([hdu3])
    lists.writeto(path + '/masterflat.fits', clobber=True)

    replacezeroes(path + '/masterflat.fits', 1.0)
    replaceNaN(path + '/masterdark.fits', 0.0)
    replaceNaN(path + '/masterbias.fits', 0.0)
    masterflat = pf.open(path + '/masterflat.fits')[0].data
    masterbias = pf.open(path + '/masterbias.fits')[0].data
    masterdark = pf.open(path + '/masterdark.fits')[0].data

    for i,f in enumerate(files_science):
        science_count +=1.
        replaceNaN(f, 0)
        reduced =  pf.open(f)[0].data
        header =  pf.open(f)[0].header

        reduced = (reduced - masterdark) / (masterflat)
        reduced = reduced [25:-25,25:-25]
        print np.mean(reduced)
        print np.max(reduced)
        print np.min(reduced)
        # plt.figure()
        # plt.imshow(reduced)
        # plt.show()

        hdu4 = pf.PrimaryHDU(reduced)
        hdu4.header = header
        hdu4.header['BZERO'] = 0.0
        lists = pf.HDUList([hdu4])


        science_name = str(f.split('/')[-1])
        science_name = ''.join(science_name)[:-5]
        lists.writeto(reduced_dir + d + '-' +science_name + '_reduced.fits', clobber=True)

    print "I have %i science images in %s" % (science_count, d)


