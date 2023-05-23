#    
#    Here we are. Finally.
#    The first main task of this script is to "put together" 
#    the right psfs for each image,
#    and complain if, for instance, one image has no psf, etc.
#    We have to look at the PSF rejection lists, as well as at the decskiplist.
#    We will do all this in memory, before touching 
#    to the database or starting anything.
#
#    Then :
#    copy the right stuff to the decdir, 
#    with the right filenames (0001, 0002, ...)
#    for identification, the "file-numbers" will be written 
#    into the db (as well as the psfname and norm coeff to use)
#
#    reference image will be put at first place, i.e. 0001
#
"""
MULTI-SETNAME UPDATE

We are making the deckey more verbose by adding the setname as well.
(the other keys built on deckey are also naturally also changed)
Then, we prepare one deconvolution per setname: this allows for the
simultaneous treatment of different bands.


THIS HAS CONSEQUENCES FOR UPDATES
the following keys, given in deconv_config_update.py (in your config dir):
    decskiplist, deckeyfilenum, deckeypsfused,
    deckeynormused, decdir, deckey
become
    decskiplists, deckeyfilenums, deckeypsfuseds,
    deckeynormuseds, decdirs, deckeys

To use an old deconv_config_update.py: rename the said variables,
and add brakets [ ] around their assigned value to make them lists. 
"""
#    
#    Do the deconvolution of all stars: one point source.
#
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))

sys.path.append('..')


from config import settings
from modules.prepare_deconvolution import prepare_deconvolution


decnormfieldname = settings['decnormfieldname']


prepare_deconvolution('lens', decnormfieldname) 