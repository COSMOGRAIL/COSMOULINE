
# This is a "settings" file for lcmanip
# It contains the configuration that will be used to convert the
# exported cosmouline database pkl into an rdb file ready for pycs.


# Filename of the exported cosmouline db :
dbfilename = "2012-01-11_f_Q1355_C2_db.pkl"

# Name of the deconvolution (see the README file that comes with the db ...) :
deconvname = "dec_wowfixback_lens_medcoeff_pyMCSabcdf1"

# Name of the pointsources of this deconvolution :
sourcenames = ["A", "B"]

# Name of the normalization coeff to use :
normcoeffname = "renormabcde"

# Telescope- and set- names that you want to process "together" :
# Do not forget some image sets, check the README to see what you have in your db !
telescopenames = ["EulerC2"]
setnames = ["1", "2"]

# Narrow the range of images you want to use (images beyond these limits are disregarded,
# i.e., not included in the nights).
imgmaxseeing = 2.5
imgmaxell = 0.3
imgmaxskylevel = 10000.0 # In electrons, not ADU !
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
nightmaxseeing = 2.5
nightmaxell = 0.2
nightmaxskylevel = 5000.0
nightmaxnormcoeff = 5.0
nightminnbimg = 1 # The minimal number of images within a night. Night flagged if number is below.


# Give a name for all your above settings. Will be used for the rdb file.
# You might want to use the telescopename, for instance.
outputname = "Q1355_EulerC2"


# Do you want to see interactive plots (otherwise I save them to file) ?
showplots = False