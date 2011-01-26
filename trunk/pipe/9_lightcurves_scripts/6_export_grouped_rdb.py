#
#	This is to export the light curve from one image.
#	quick and dirty test for now... not yet the clean way
#
#	we export GROUPED images
#


toexport = ('dec_full2_lens_medcoeff_abcikm1','A')
filename = "A.txt"

#errorname = "magerror_1256"





# - - - - - - - - - - - - - - - - - - - - - - - 

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from combibynight_fct import *
#from star import *
from rdbexport import *


from numpy import *

db = KirbyBase()

deckey = toexport[0]
sourcename = toexport[1]
deckeyfilenum = "decfilenum_" + deckey
intfieldname = "out_" + deckey + "_" + sourcename + "_flux"

images = db.select(imgdb, ["gogogo", "treatme", deckeyfilenum], [True, True, '\d\d*'], returnType='dict', useRegExp=True)

#images = db.select(imgdb, ["gogogo", "treatme", deckeyfilenum, "seeing"], [True, True, '\d\d*', "<1.8"], returnType='dict', useRegExp=True)

print "I will export a lightcurve for ", len(images), "images."
#proquest(askquestions)

groupedimages = groupbynights(images, separatesetnames=True)

groupedmags = mags(groupedimages, intfieldname)['median']
groupederrors = list((array(mags(groupedimages, intfieldname)['max']) - array(mags(groupedimages, intfieldname)['min'])) / 2.0)



#groupederrors = asarray(values(groupedimages, errorname)['mean'])
#lengths = array(map(len, groupedimages))
#groupederrors = 2.0*groupederrors / sqrt(lengths)
#groupederrors = list(groupederrors)

telescopes = map(lambda x : x[0]["telescopename"], groupedimages)
mhjds = values(groupedimages, "mhjd")['mean']


columns = [{"name":"telescope", "data":telescopes}, {"name":"mhjd", "data":mhjds}, {"name":"magnitude", "data":groupedmags}, {"name":"magerror", "data":groupederrors}]
writerdb(columns, filename)


sys.exit()



	
