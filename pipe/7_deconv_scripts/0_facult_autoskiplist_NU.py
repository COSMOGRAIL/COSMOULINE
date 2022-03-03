#    Tiny helper to ouput a list of images to skip for a particular 
#   deconvolution, according to very simple criteria specified below.
#    This is perfectly facultative !

#    Do this for the lens, no need to run it for the renormalization stars etc 
#   (as the bad images will be skiped for the lens anyway)

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import imgdb, settings, configdir
from modules.variousfct import proquest, readimagelist
from modules.kirbybase import KirbyBase

askquestions = settings['askquestions']

if settings['update']:
    askquestions = False
    # override config settings...
    sys.path.append(configdir)
    from deconv_config_update import decskiplist
else:
    from config import decskiplist




########## Configuration #########
showhist = False

if 1:
    # Normal rejection stuff :
    maxseeing = 2.5
    maxell = 0.25
    maxmedcoeff = 3.0
    maxsky = 8000.0
 
if 0:
    # strict rejection stuff :
    maxseeing = 1.
    maxell = 0.2
    maxmedcoeff = 3.0
    maxsky = 8000.0 
    
    


if 0:
    # The very best frames to draw a good background :
    maxseeing = 0.8
    maxell = 0.12
    maxmedcoeff = 1.28
    maxsky = 550.0


'''
# NTT rejection :
maxseeing = 1.2
maxell = 0.12
maxmedcoeff = 2.0
maxsky = 6000.0
'''

'''
# VLT rejection stuff (WIP) :
maxseeing = 1.2
maxell = 0.25
maxmedcoeff = 1.2
maxsky = 5000.0
'''

'''
# VLT best (WIP) :
maxseeing = 0.43
maxell = 0.06
maxmedcoeff = 1.0
maxsky = 1000
'''



##################################


print("You can configure some lines right at the beginning of this script.")



db = KirbyBase(imgdb)


images = db.select(imgdb, ['gogogo', 'treatme'], 
                          [True, True],
                          returnType='dict', 
                          sortFields=['setname', 'mjd'])

nbtot = len(images)

if os.path.isfile(decskiplist):
    print("You already have a decskiplist.")
    print("Good for you. But I don't care",
         "(change me in the script itself if needed)")
    if 0:
        print("In this script I will only consider images that",
              "are not yet rejected by this decskiplist.")
        decskipimgnames = [image[0] for image in readimagelist(decskiplist)] 
        # (image[1] would be the comment)
        images = [image for image in images 
                         if image["imgname"] not in decskipimgnames]
        
    print("Full path to decskiplist :")
else:
    cmd = "touch " + decskiplist
    os.system(cmd)
    print("I have just touched the decskiplist for you :")
    
print(decskiplist)

print("Note that here I do not look at a particular extracted object,",
      "but at the full database.")
print("Looking at which object / PSFs are available for each image",
      "will be done in the next script.")
print(f"We have {len(images)} images with gogogo=True, treatme=True,",
      "and not yet on the decskiplist.")



if showhist :
    setnames = list(set([image["setname"] for image in images]))
    print(f"setnames : {', '.join(setnames)}")

    print("Some histograms. Close the graphs to continue.")
    plt.figure(1)
    seeinglists = [np.array([image["seeing"] for image in images 
                                    if image["setname"] == setname]) 
                                                for setname in setnames]
    plt.hist(seeinglists, bins=30)
    plt.axvline(maxseeing, color="red")
    plt.xlabel("Seeing [arcsec]")

    plt.figure(2)
    elllists = [np.array([image["ell"] for image in images 
                                    if image["setname"] == setname]) 
                                                for setname in setnames]
    plt.hist(elllists, bins=30)
    plt.axvline(maxell, color="red")
    plt.xlabel("Ellipticity")

    plt.figure(3)
    medcoefflists = [np.array([image["medcoeff"] for image in images 
                                         if image["setname"] == setname]) 
                                                  for setname in setnames]
    plt.hist(medcoefflists, bins=30)
    plt.axvline(maxmedcoeff, color="red")
    plt.xlabel("Medcoeff")

    plt.figure(4)
    skylists = [np.array([image["skylevel"] for image in images 
                                       if image["setname"] == setname]) 
                                                  for setname in setnames]
    plt.hist(skylists, bins=30)
    plt.axvline(maxsky, color="red")
    plt.xlabel("Sky level")
    
    plt.show()



print("\nHere are the images that do not satisfy your criteria",
      "(order of rejection : seeing, ell, medcoeff) :\n\n\n")
 

rejlines = []
rejectimages = [image for image in images if image["seeing"] > maxseeing]
rejlines.extend([f"{image['imgname']}\t\tseeing = {image['seeing']:.2f} arcsec" 
                                                    for image in rejectimages])
images = [image for image in images if image not in rejectimages] 


rejectimages = [image for image in images if image["ell"] > maxell]
rejlines.extend([f"{image['imgname']}\t\tell = {image['ell']:.2f}" 
                                                    for image in rejectimages])
images = [image for image in images if image not in rejectimages] 


rejectimages = [image for image in images if image["medcoeff"] > maxmedcoeff]
rejlines.extend([f"{image['imgname']}\t\tmedcoeff = {image['medcoeff']:.2f}" 
                                                    for image in rejectimages])
images = [image for image in images if image not in rejectimages] 


rejectimages = [image for image in images if image["skylevel"] > maxsky]
rejlines.extend([f"{image['imgname']}\t\tskylevel = {image['skylevel']:.2f}" 
                                                    for image in rejectimages])
images = [image for image in images if image not in rejectimages] 


print(f"# Autoskiplist made with maxseeing = {maxseeing:.3f},",
      f"maxell = {maxell:.3f}, maxmedcoeff = {maxmedcoeff:.3f},",
      f"maxsky = {maxsky:.1f} .")

print(f"# It contains {len(rejlines)} images.")
print("\n".join(rejlines))

print(f"\n\n\nAutoskiplist made with maxseeing = {maxseeing:.3f},",
      f"maxell = {maxell:.3f}, maxmedcoeff = {maxmedcoeff:.3f},",
      f"maxsky = {maxsky:.1f} .")
print(f"It contains {len(rejlines)} images, out of {nbtot}")
print(f"Number of images potentially left : {nbtot - len(rejlines)}")

print("I can copy and paste this into your decskiplist,",
      "if you want to skip them.")
proquest(askquestions)
with open(decskiplist, 'w') as skiplist:
    skiplist.write('\n')
    skiplist.write("\n".join(rejlines))
print("OK, done")

