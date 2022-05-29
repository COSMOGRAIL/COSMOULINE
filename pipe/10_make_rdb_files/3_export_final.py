
import sys
import os
from os.path import join
from shutil import copy, move
from glob import glob
from pathlib import Path


if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import settings, configdir, deckeys


telescopename = settings['telescopename']
decobjname = settings['decobjname']
workdir = settings['workdir']
refimgname_per_band = settings['refimgname_per_band']
decpsfnames = settings['decpsfnames']
psfname = settings['psfname']
combibestname = settings['combibestname']
setnames = settings['setnames']
lensName = settings['lensName']
#%%

if telescopename == "EulerCAM" :
    telescopename = "ECAM"

elif telescopename == "EulerC2" :
    telescopename = "C2"

if not os.path.exists(configdir + "/export_final" ):
    os.makedirs(configdir + "/export_final")

exportdir = join(configdir, "export_final")

if decobjname == "lens" :
    for deckey, setname in zip(deckeys, setnames):
        refimgname = refimgname_per_band[setname]
        refdeconvpng = join(workdir, f"{deckey}_png", f"{refimgname}.png")
        copytopath = join(exportdir, f"{telescopename}_{deckey}_ref.png")
        copy(refdeconvpng, copytopath)
else:
    print("I didn't copy the deconvolution of the ref image : CHANGE the decobjname in setting.py ! ")
#%%
if decpsfnames[0] == psfname :
    for deckey, setname in zip(deckeys, setnames):
        refimgname = refimgname_per_band[setname]
        refpsfpng = join(workdir, f"psf_{psfname}_png", f"{refimgname}.png")
        copytopath = join(exportdir, f"{telescopename}_psf_{psfname}_ref.png")
        copy(refpsfpng, copytopath)
else :
    print("I don't know which psf name to chose : CHANGE the psfname or decpsfnames in your setting.py")
#%%
main_name = settings['outputname']

# 844_combi_best1
### copying the stacks
for setname in setnames:
    combipathbase = join(workdir, f"{setname}_combi_{combibestname}")
    newcombibase = join(exportdir, f"{telescopename}_{setname}_combi_{combibestname}")
    for ext in ['.fits', '.png']:
        copy(combipathbase+ext, newcombibase+ext)
#%%
    
# copying the database pickle, RDB files and settings
pklname = f"{main_name}_db.pkl"
rdbname = f"{main_name}.rdb"
settingsname = "settings.py"
for ff in [pklname, rdbname, settingsname]:
    copy( join(configdir, ff), join(exportdir, ff) )
#%%
# copying the readme and plots
readmes     = glob( join(configdir, "*_readme.txt") )
seeingplots = glob( join(configdir, "*_median_seeing.png") )
plots       = glob( join(configdir, "*_plot.pdf") )

for ff in (readmes + seeingplots + plots):
    copy(ff, exportdir)
    
(Path(exportdir) / f"{telescopename}_README.txt").touch()
print("I touched the README for you, please write something in there.")


nicefielddir = join(exportdir, "nicefields")
if not os.path.exists(nicefielddir) :
    os.makedirs(nicefielddir)
    
# copy crops of the lens:
for setname in setnames:
    nicecrop = Path(workdir) / f"{setname}_obj_lens_ref_input.fits"
    if not nicecrop.exists():
        print("Warning!")
        print(f"I did not find the lens-crop (dec input) for setname {setname}")
        print()
    else:
        newname = f"{main_name}_zoom.fits"
        copy(nicecrop, join(nicefielddir, newname))
#%%
# copy the main result plot (the light curves) made in the previous script:
baselcname = f"{settings['outputname']}_Light_Curve"
for ext in ['.pdf', '.png']:
    copy( join(configdir, baselcname + ext), exportdir)

