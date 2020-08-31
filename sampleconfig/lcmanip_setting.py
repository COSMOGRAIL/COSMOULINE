
# This is a "settings" file for lcmanip
# It contains the configuration that will be used to convert the
# exported cosmouline database pkl into an rdb file ready for pycs.


################### Settings common to all operations ##################

# Filename of the exported cosmouline db :
dbfilename = "2018-12-19_J1721_Maidanak_db.pkl"

# Name of the deconvolution (see the README file that comes with the db ...) :
deconvname = "dec_backfull_lens_renorm_abdefgknps_abdekn"


################### Section for addfluxes.py ###########################

toaddsourcenames = ["A1", "A2"] # Name of the sources whose fluxes you want to add

sumsourcename = "A" # Name of the resulting source
# This new source will get added to the db as if it would have come from a deconv.


################### Section for join.py ################################

# Name of the pointsources of this deconvolution :
sourcenames = ["A", "B","C","D"]

# Name of the normalization coeff to use :
normcoeffname = "renorm_abdefgknps"
# In principle it is also ok to put "medcoeff", as for the renorm itself it works in the same way.
# Note : aside of the coefficients alone, we also read the fields (example) :
# renormabcfg1_err	float, absolute error on the coeff
# renormabcfg1_comment	string of ints, like "5" giving the number of stars for this coeff.

# Telescope- and set- names that you want to process "together" :
# Do not forget some image sets, check the README to see what you have in your db !
telescopenames = ["EulerCAM"]
setnames = ["1","2","3"]

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
showplots = True
