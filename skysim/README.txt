Quick tutorial :

We need python, numpy, pyfits.

Install skymaker somewhere on your computer (is already done on obssr1, just go on).

cd pipe

cp sampleconfig.py config.py

Edit this config.py, set the path to the skymaker bin, and a path to an existing directory where you want
the images to be written.

cp sampleconfig.sky config.sky

This config.sky contains all the default settings that you want for your images.
You could change them of course, but leave the defaults for a first run.

Then :

python build_sourcelist_default.py
This builds a list of sources, in this case PSF stars and some targets to deconvolve.

python draw_seeingramp.py
This generates the acutal fits images.

