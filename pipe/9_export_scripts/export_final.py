import os

execfile("../config.py")
if telescopename == "EulerCAM" :
    telescopename = "ECAM"

elif telescopename == "EulerC2" :
    telescopename = "C2"

if not os.path.exists(configdir + "/export_final" ):
    os.makedirs(configdir + "/export_final")

exportdir = configdir + "/export_final"

if decobjname == "lens" :
    os.system("cp " + workdir + "/" + deckey + "_png/" + refimgname + ".png " + exportdir )
    os.system("mv " + exportdir + "/" + refimgname + ".png " + exportdir + "/" + telescopename + "_" + deckey + "_ref.png" )
else:
    print "I didn't copy the deconvolution of the ref image : CHANGE the decobjname in setting.py ! "

if decpsfnames[0] == psfname :
    os.system("cp " + workdir + "/psf_" + psfname + "_png/" + refimgname + ".png " + exportdir)
    os.system("mv " + exportdir + "/" + refimgname + ".png " + exportdir + "/" + telescopename + "_psf_" + psfname + "_ref.png")
else :
    print "I don't know which psf name to chose : CHANGE the psfname or decpsfnames in your setting.py"

os.system("cp " + workdir +"/alistars.png " + exportdir)
os.system("mv " + exportdir +"/alistars.png " + exportdir+"/"+telescopename+"_alistar.png")
os.system("cp " + workdir +"/combi_" + combibestname + ".fits " + exportdir)
os.system("cp " + workdir +"/combi_" + combibestname + ".png " + exportdir)
os.system("cp " + workdir +"/combi_" + combibestname + "_log.txt " + exportdir)
os.system("mv " + exportdir +"/combi_" + combibestname +".fits " + exportdir+"/"+telescopename+"_combi_" + combibestname + ".fits")
os.system("cp " + configdir+"/" + os.path.split(configdir)[-1] + "_db.pkl " + exportdir)
os.system("cp " + configdir + "/lcmanip_setting.rdb " + exportdir)
os.system("mv " + exportdir + "/lcmanip_setting.rdb " + exportdir+ "/" + os.path.split(configdir)[-1] + ".rdb")
os.system("cp " + configdir + "/*_readme.txt " + exportdir)
os.system("mv " + configdir + "/*_median_seeing.png " + exportdir)
os.system("mv " + configdir + "/*_plot.pdf " + exportdir)
os.system("touch " + exportdir + "/" + telescopename + "_README.txt" )
print "I touched the README for you, please write something in there."


if not os.path.exists(exportdir + "/nicefields"):
    os.makedirs(exportdir + "/nicefields")

nicefielddir = exportdir + "/nicefields"
os.system("cp " + workdir + "/obj_lens_ref_input.fits " + nicefielddir)
os.system("mv " + nicefielddir +"/obj_lens_ref_input.fits " + nicefielddir +"/" +os.path.split(configdir)[-1] + "_zoom.fits")
os.system("mv " + exportdir +"/combi_" + combibestname +".png " + nicefielddir+"/"+telescopename+"_field.png")

print "Hey, you still have to make the light curve with plot_lcs.py and export them in png and pdf"
print "You also need to make the nicefield image "

# if computer == "martin":
#     print "Hey, I can also copy the database.rdb in your TD_measure folder"
#     proquest(True)
#     os.system("cp " + exportdir+ "/" + os.path.split(configdir)[-1] + ".rdb "+ "~/Desktop/TD_measure")








