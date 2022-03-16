execfile("../config.py")
import os
from variousfct import *
import star


photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)

print "I will run a full deconvolution for the following stars:"
print [star.name for star in photomstars]
proquest(True)

if thisisatest == False:
    print "Warning : This is NOT a test !"
    print "You did not forget to update your photomstar.cat with only the good stars, right ?"
    proquest(True)

for star in photomstars :
    os.system("python 1_prepfiles.py " + star.name)
    os.system("python 2_applynorm_NU.py " + star.name)
    os.system("python 3_fillinfile_NU.py "+ star.name)
    os.system("python 4_deconv_NU.py "+ star.name)
    os.system("python 5b_showptsrc_NU.py " + star.name)
    os.system("python 5a_decpngcheck_NU.py "+ star.name)
    
    if computer == "regor4" :
		if not os.path.exists(visudir + "/dec_psf_" + decpsfnames[0] + "/dec_" + star.name): 
			os.makedirs(visudir + "/dec_psf_" + decpsfnames[0] + "/dec_" + star.name)
			print visudir + "/dec_psf_" + decpsfnames[0] + "/dec_" + star.name
		
		print "I'll copy the png to your visudir !"
		key = "dec_" + decname + "_" + star.name + "_" + decnormfieldname + "_" + "_".join(decpsfnames)
		os.system("cp "+workdir+"/"+key+ "_png/"+"0*.png " + visudir + "/dec_psf_" + decpsfnames[0] + "/dec_" + star.name)

if thisisatest == False: 
	print "You can now check the png and readout the good stars."
