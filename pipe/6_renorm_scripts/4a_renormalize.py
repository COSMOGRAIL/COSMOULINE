import progressbar
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from astropy.stats import sigma_clip
sys.path.append(os.path.dirname(sys.path[0]))
sys.path.append('..')
from config import imgdb, settings, plotdir, dbbudir,\
                   normerrfieldname, normcommentfieldname
from modules.variousfct import proquest, backupfile
from modules.kirbybase import KirbyBase

db = KirbyBase(imgdb, fast=True)

askquestions = settings['askquestions']
normname = settings['normname']
allnormsources = settings['normsources']
setnames = settings['setnames']


print("You want to calculate a normalization coefficient called:")
print(normname)
print("using the sources")
for normsource in allnormsources[0]:
    print(normsource)


refimgname_per_band = settings['refimgname_per_band']


allimages = []

for setname, normsources in zip(setnames, allnormsources):
    print(" --------- " + setname + " --------- ")
    refimgname = refimgname_per_band[setname]
    # Sort them like this, to ensure that points of one night are side by side
    # (looks better on graphs ...)

    bandimages = db.select(imgdb, ['gogogo', 'treatme', 'setname'], 
                             [True, True, setname], 
                             returnType='dict', 
                             sortFields=['mhjd'])
    
    telescopenames = sorted(list(set([image["telescopename"] 
                                            for image in bandimages])))
    
    
    for image in bandimages:
        image["tmp_indivcoeffs"] = []
        image["tmp_indivcoeffserr"] = []
    
    
    for telescopename in telescopenames:
        print(" --- " + telescopename + " --- ")
        
        colorrefmedflux = 0.0
        
        telimages = [image for image in bandimages 
                            if image["telescopename"] == telescopename]
        print(f"{len(telimages)} images")
        
        for j, normsource in enumerate(normsources):
            deckey = normsource[0]
            sourcename = normsource[1]
            deckeyfilenumfield = f"decfilenum_{deckey}"
            fluxfieldname = f"out_{deckey}_S_flux"
            errorfieldname = f"out_{deckey}_S_shotnoise"
            
            sourcetelimages = [image for image in telimages 
                                     if image[deckeyfilenumfield] != None]
            print(f"{deckey:20} {sourcename:5} : {len(sourcetelimages):4}",
                   "deconvolutions available")
        
            # So these are raw fluxes in electrons, not normalized:
            fluxes  = np.array([image[fluxfieldname] 
                                  for image in sourcetelimages]) 
            dfluxes = np.array([image[errorfieldname] 
                                  for image in sourcetelimages]) 
            # This is the plain simple unnormalized ref flux
            # that we will use for this star.
            medflux = np.median(fluxes) 
            
            # For the first star, this will be the colorrefmedflux :
            if j == 0:
                print("(That's the colour ref source.)\n")
                colorrefmedflux = medflux
        
            for image in sourcetelimages:
                    # the "new" absolute coeff for that image and star
                    indivcoeff = medflux / image[fluxfieldname]
                    dindivcoeff = medflux / image[fluxfieldname]**2 * image[errorfieldname]
                    image["tmp_indivcoeffs"].append(indivcoeff)
                    image["tmp_indivcoeffserr"].append(dindivcoeff)
                
    
        for i, image in enumerate(telimages):
        
            if len(image["tmp_indivcoeffs"]) == 0:
                # bummer. Then we will just write 0.0, 
                # to be sure that this one will pop out.
                normcoeff = 0.0
                normcoefferr = 0.0
                
            else :
                # weighted average with rejection
                _coeffs = np.array(image["tmp_indivcoeffs"])
                _dcoeffs = np.array(image["tmp_indivcoeffserr"])
                clipped = sigma_clip(_coeffs, sigma=3)
                
                filtered_weights = 1./_dcoeffs[~clipped.mask]
                filtered_values = _coeffs[~clipped.mask]
                normcoeff = np.average(filtered_values,
                                         weights=filtered_weights)
                weighted_variance = np.sum(filtered_weights * (filtered_values - normcoeff) ** 2) / np.sum(filtered_weights)
                normcoefferr = weighted_variance**0.5
                
                
            
            #  the important value at this step:
            image["tmp_coeff"] = normcoeff 
            image["tmp_coefferr"] = normcoefferr
            # now each image has such a tmp_coeff.
    
    
            # Now, we want to apply a simple scaling to these coeffs 
            # between the telescopes, so that a choosen star gets 
            # the same median flux.
            # this number will be small, but we don't care:
            image["tmp_coeff"] /= colorrefmedflux
            image["tmp_coefferr"] /= colorrefmedflux
            
            
    
    
    # Finally, we rescale the coeffs so that the ref image gets 1.0
    
    refimage = [image for image in bandimages 
                       if image["imgname"] == refimgname][0]
    
    if len(refimage["tmp_indivcoeffs"]) == 0:
        print("You did not deconvolve the reference image.")
        print("Warning: I will not scale the",
              "normalization coeffs as usual!")
        
        refnewcoeff = np.median(np.array([image["tmp_coeff"] 
                                          for image in bandimages]))
    
    else:
        refnewcoeff = refimage["tmp_coeff"]
        
    for image in bandimages:
        image["normcoeff"] = image["tmp_coeff"] / refnewcoeff
        image["normcoefferr"] = image["tmp_coefferr"] / refnewcoeff
        
        # And we keep track of the number of stars used
        # to calculate this particular coeff:
        image["nbcoeffstars"] = len(image["tmp_indivcoeffs"])
            
    
    
    
    # gather the treated images in allimages:
    allimages += bandimages
    # sets figure size
    plt.figure(figsize=(15,15))
    
    normcoeffs = np.array([image["normcoeff"] for image in bandimages])
    errs = np.array([image["normcoefferr"] for image in bandimages])
    

    
    plt.errorbar(np.arange(len(normcoeffs)), 
                 normcoeffs, yerr=errs,
                 linestyle="None", 
                 marker=".", 
                 label=normname, 
                 color="red")
    
    # and show the plot
    
    plt.xlabel('Images')
    plt.ylabel('Coefficient')
    
    plt.grid(True)
    plt.legend()
    plt.title(setname)
    
    if settings['savefigs']:
        plotfilepath = os.path.join(plotdir, 
                           f"norm_{setname}_{normname}.pdf")
        plt.savefig(plotfilepath)
        print(f"Wrote {plotfilepath}")
    else:
        plt.show()
    
    
    
    
print("Ok, I will now add these coefficients to the database.")
proquest(askquestions)

# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, normname)




if normname in db.getFieldNames(imgdb):
    print("The field", normname, "already exists in the database.")
    print("I will erase it.")
    proquest(askquestions)
    db.dropFields(imgdb, [normname])
    if normerrfieldname in db.getFieldNames(imgdb):
        db.dropFields(imgdb, [normerrfieldname])
    if normcommentfieldname in db.getFieldNames(imgdb):
        db.dropFields(imgdb, [normcommentfieldname])

db.pack(imgdb) # to erase the blank lines

db.addFields(imgdb, [f'{normname}:float', 
                     f'{normerrfieldname}:float', 
                     f'{normcommentfieldname}:str'])

widgets = [progressbar.Bar('>'), ' ',
           progressbar.ETA(), ' ',
           progressbar.ReverseBar('<')]
pbar = progressbar.ProgressBar(widgets=widgets, 
                               maxval=len(allimages)+2).start()

for i, image in enumerate(allimages):
    pbar.update(i)
    db.update(imgdb, ['recno'], 
                     [image['recno']], 
                     {normname: float(image["normcoeff"]), 
                      normerrfieldname : float(image["normcoefferr"]), 
                      normcommentfieldname: str(int(image["nbcoeffstars"]))})

pbar.finish()

db.pack(imgdb) # to erase the blank lines

print("Ok, here you are.")
