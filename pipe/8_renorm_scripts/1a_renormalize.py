import progressbar
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
from config import imgdb, settings, plotdir, dbbudir
from modules.variousfct import proquest, backupfile
from modules.kirbybase import KirbyBase

db = KirbyBase(imgdb)

askquestions = settings['askquestions]']
renormname = settings['renormname']
renormsources = settings['renormsources']


print("You want to calculate a renormalization coefficient called:")
print(renormname)
print("using the sources")
for renormsource in renormsources:
    print(renormsource)

db = KirbyBase(imgdb)

# Sort them like this, to ensure that points of one night are side by side
# (looks better on graphs ...)
allimages = db.select(imgdb, ['gogogo', 'treatme'], 
                             [True, True], 
                             returnType='dict', 
                             sortFields=['setname', 'mhjd'])

telescopenames = sorted(list(set([image["telescopename"] 
                                        for image in allimages])))


for image in allimages:
    image["tmp_indivcoeffs"] = []


for telescopename in telescopenames:
    print(" --- " +telescopename + " --- ")
    
    colorrefmedflux = 0.0
    
    telimages = [image for image in allimages 
                        if image["telescopename"] == telescopename]
    print(f"{len(telimages)} images")
    
    for j, renormsource in enumerate(renormsources):
        deckey = renormsource[0]
        sourcename = renormsource[1]
        deckeyfilenumfield = "decfilenum_" + deckey
        fluxfieldname = "out_" + deckey + "_" + sourcename + "_flux"
        errorfieldname = "out_" + deckey + "_" + sourcename + "_shotnoise"
        
        sourcetelimages = [image for image in telimages 
                                 if image[deckeyfilenumfield] != None]
        print(f"{deckey:20} {sourcename:5} : {len(sourcetelimages):4}",
               "deconvolutions available")
    
        # So these are raw fluxes in electrons, not normalized:
        fluxes = np.array([image[fluxfieldname] for image in sourcetelimages]) 
        
        # This is the plain simple unnormalized ref flux
        # that we will use for this star.
        medflux = np.median(fluxes) 
        
        # For the first star, this will be the colorrefmedflux :
        if j == 0:
            print("That's the colour ref source.")
            colorrefmedflux = medflux
    
        for image in sourcetelimages:
                # the "new" absolute coeff for that image and star
                indivcoeff = (medflux / image[fluxfieldname])
                image["tmp_indivcoeffs"].append(indivcoeff)
            

    for i, image in enumerate(telimages):
    
        if len(image["tmp_indivcoeffs"]) == 0:
            # bummer. Then we will just write 0.0, 
            # to be sure that this one will pop out.
            renormcoeff = 0.0
            renormcoefferr = 0.0
            
        else :
            # median of multiplicative factors
            renormcoeff = np.median(np.array(image["tmp_indivcoeffs"])) 
            renormcoefferr = np.std(np.array(image["tmp_indivcoeffs"]))
        
        #  the important value at this step:
        image["tmp_coeff"] = renormcoeff 
        image["tmp_coefferr"] = renormcoefferr
        # now each image has such a tmp_coeff.


        # Now, we want to apply a simple scaling to these coeffs 
        # between the telescopes, so that a choosen star gets 
        # the same median flux.
        # this number will be small, but we don't care:
        image["tmp_coeff"] /= colorrefmedflux
        image["tmp_coefferr"] /= colorrefmedflux
        
        


# Finally, we rescale the coeffs so that the ref image gets 1.0

refimage = [image for image in allimages 
                   if image["imgname"] == refimgname][0]

if len(refimage["tmp_indivcoeffs"]) == 0:
    print("You did not deconvolve the reference image.")
    print("Warning: I will not scale the",
          "renormalization coeffs as usual!")
    
    refnewcoeff = np.median(np.array([image["tmp_coeff"] 
                                      for image in allimages]))

else:
    refnewcoeff = refimage["tmp_coeff"]
    
for image in allimages:
    image["renormcoeff"] = image["tmp_coeff"] / refnewcoeff
    image["renormcoefferr"] = image["tmp_coefferr"] / refnewcoeff
    
    # And we keep track of the number of stars used
    # to calculate this particular coeff:
    image["nbcoeffstars"] = len(image["tmp_indivcoeffs"])
        


plt.figure(figsize=(15,15))    # sets figure size

medcoeffs = np.array([image["medcoeff"] for image in allimages])
renormcoeffs = np.array([image["renormcoeff"] for image in allimages])

plt.semilogy(medcoeffs, linestyle="None", 
                        marker=".", 
                        label="medcoeff", 
                        color="black")

plt.semilogy(renormcoeffs, linestyle="None", 
                           marker=".", 
                           label=renormname, 
                           color="red")

# and show the plot

plt.xlabel('Images (by setname, then date)')
plt.ylabel('Coefficient')

plt.grid(True)
plt.legend()

if settings['savefigs']:
    plotfilepath = os.path.join(plotdir, 
                                f"renorm_{renormname}_medcoeffcompa.pdf")
    plt.savefig(plotfilepath)
    print(f"Wrote {plotfilepath}")
else:
    plt.show()




# If you want, you can now write this into the database.

print("Ok, I would now add these coefficients to the database.")
proquest(askquestions)


# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, renormname)


if renormname in db.getFieldNames(imgdb):
    print("The field", renormname, "already exists in the database.")
    print("I will erase it.")
    proquest(askquestions)
    db.dropFields(imgdb, [renormname])
    if renormerrfieldname in db.getFieldNames(imgdb):
        db.dropFields(imgdb, [renormerrfieldname])
    if renormcommentfieldname in db.getFieldNames(imgdb):
        db.dropFields(imgdb, [renormcommentfieldname])

db.pack(imgdb) # to erase the blank lines

db.addFields(imgdb, [f'{renormname}:float', 
                     f'{renormerrfieldname}:float', 
                     f'{renormcommentfieldname}:str'])

widgets = [progressbar.Bar('>'), ' ',
           progressbar.ETA(), ' ',
           progressbar.ReverseBar('<')]
pbar = progressbar.ProgressBar(widgets=widgets, 
                               maxval=len(allimages)+2).start()

for i, image in enumerate(allimages):
    pbar.update(i)
    db.update(imgdb, ['recno'], 
                     [image['recno']], 
                     {renormname: float(image["renormcoeff"]), 
                      renormerrfieldname : float(image["renormcoefferr"]), 
                      renormcommentfieldname: str(int(image["nbcoeffstars"]))})

pbar.finish()

db.pack(imgdb) # to erase the blank lines

print("Ok, here you are.")
