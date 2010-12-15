Quick tutorial :


Install skymaker somewhere on your computer (is already done on obssr1, just go on).

cd pipe

cp sampleconfig.py config.py

Edit this config.py, set the path to the skymaker bin, and a path to an existing directory where you want
the images to be written.

cp sampleconfig.sky config.sky

This config.sky contains all the default settings that you want for your images.
You could change them of course, but leave the defaults for a first run.


Then, for a first run :

python build_sourcelist_default.py
python draw_seeingramp.py
