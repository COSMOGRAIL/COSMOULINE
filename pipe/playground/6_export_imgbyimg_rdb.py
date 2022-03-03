#
#	We export some fields from the database into a tab separated rdb file, line by line, as simple as possible.
#	Can be used for further processing by third party software
#
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))

# - - - - - - - - - - - - - - - - - - - - - - -
#	OPTIONAL CONFIGURATION
# - - - - - - - - - - - - - - - - - - - - - - -

selectiondeckey = deckey # Leave deckey -> we use the current setting from settings.py.

generalfields = ["imgname", "mhjd", "datet", "airmass", "seeing", "skylevel"]

# The fluxes of your sources will be added automatically, as well as a field called "decnormcoeff", containing
# the actual normalization coefficients that were used for your deconvolution.

writeheader = True

outputfilename = "imgbyimg_%s.rdb" % selectiondeckey

# - - - - - - - - - - - - - - - - - - - - - - - 


from kirbybase import KirbyBase, KBError
from variousfct import *
from combibynight_fct import *
from rdbexport import *
import star
import numpy as np


db = KirbyBase(imgdb)

images = db.select(imgdb, ["gogogo", "treatme", "decfilenum_" + selectiondeckey], [True, True, '\d\d*'], returnType='dict', useRegExp=True)

print("I will export the deconvolution %s" % selectiondeckey)
print("This corresponds to ", len(images), "images.")

# We extend these general fields by the flux measurements for the selected deconvolution.
ptsrc = star.readmancat(os.path.join(configdir, selectiondeckey + "_ptsrc.cat"))
print("Sources : " + ", ".join([src.name for src in ptsrc]))
proquest(askquestions)


generalcolumns = [{"name":fieldname, "data":[image[fieldname] for image in images]} for fieldname in generalfields]

generalcolumns.append({"name":"decnormcoeff", "data":[image["decnorm_" + selectiondeckey] for image in images]})
# This field called "decnormcoeff" is the actual normalization coefficients used for your deconvolution.

specialcolumns = [{"name": "rawflux_" + src.name, "data":[image['out_' + selectiondeckey + '_'+ src.name +'_flux'] for image in images]} for src in ptsrc]
specialcolumns.extend([{"name": "normflux_" + src.name, "data":[image['out_' + selectiondeckey + '_'+ src.name +'_flux']*image["decnorm_" + selectiondeckey] for image in images]} for src in ptsrc])

writerdb(generalcolumns + specialcolumns, outputfilename, writeheader)

print("Wrote %s" % outputfilename)	
