
# This is a "settings" file for lcmanip
# It contains the configuration that will be used to convert the
# exported cosmouline database pkl into an rdb file ready for pycs.


# Filename of the exported cosmouline db :
dbfilename = "2012-01-09_f_Q1355_C2_db.pkl"

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

# Narrow the range of images you want to use (images beyond these limits are disregarded).
imgmaxseeing = 2.5
imgmaxell = 0.3
imgmaxskylevel = 10000.0 # In electrons
imgmaxmedcoeff = 8.0

# Narrow the range of nights you want to use (values are the medians among the images in a night).
# Nights beyond these limits are flagged, not removed !
nightmaxseeing = 2.0
nightmaxskylevel = 5000.0



