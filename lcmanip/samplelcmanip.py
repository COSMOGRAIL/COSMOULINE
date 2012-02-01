
# This is a "settings" file for lcmanip
# It contains the configuration that will be used to convert the
# exported cosmouline database pkl into an rdb file ready for pycs.


# Filename of the exported cosmouline db :
dbfilename = "2012-01-11_f_Q1355_C2_db.pkl"

# Name of the deconvolution (see the README file that comes with the db ...) :
deconvname = "dec_wow_lens_medcoeff_pyMCSabcdf1"

# Name of the pointsources of this deconvolution :
sourcenames = ["A", "B"]

# Name of the normalization coeff to use :
normcoeffname = "renormabcde1"
# In principle would be ok to put "medcoeff", as for the renorm itself it works in the same way, but
# a calculation of the error on medcoeff is not implemented, so scripts may fail.


# Telescope- and set- names that you want to process "together" :
# Do not forget some image sets, check the README to see what you have in your db !
telescopenames = ["EulerC2"]
setnames = ["1"]

# Narrow the range of images you want to use (images beyond these limits are disregarded,
# i.e., not included in the nights).
imgmaxseeing = 3.0
imgmaxell = 0.4
imgmaxrelskylevel = 10000.0 # In electrons, for a normalization of 1.0 (i.e. ref image)
imgmaxmedcoeff = 8.0

# Additionally, you can use a skiplist.
# Same "format" as for cosmouline, i.e. one imgname per line + facult comment.
# Example :
# 1_C2.2010-08-03T01:14:52.000     I don't like this one
# To use such a list, give the filename (not the full path) below, and put the file into 
# the lcmanipdir.

imgskiplistfilename = None
#imgskiplistfilename = "skiplist.txt"

# Narrow the range of nights you want to use (values are the medians among the images in a night).
# Nights beyond these limits are flagged, not removed !
nightmaxseeing = 2.2
nightmaxell = 0.25
nightmaxrelskylevel = 5000.0 # Skylevel in electrons, for a normalization of 1.0 (i.e. ref image)
nightmaxnormcoeff = 2.0
nightminnbimg = 3 # The minimal number of images within a night. Night flagged if number is below.


# Do you want me to write the usual 2 header lines into my rdb files ?
writeheader = True
# Do you want to see interactive plots (otherwise I save them to file) ?
showplots = False
