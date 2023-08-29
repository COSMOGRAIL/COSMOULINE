# here have to use WCS and take cutouts before stacking.
# use the largest possible field stored in the database table `common_wcs`




# import numpy as np
# from astropy.io import fits
# import sys
# import os
# if sys.path[0]:
#     # if ran as a script, append the parent dir to the path
#     sys.path.append(os.path.dirname(sys.path[0]))
# else:
#     # if ran interactively, append the parent manually as sys.path[0] 
#     # will be emtpy.
#     sys.path.append('..')
# from config import imgdb, settings, alidir
# from modules.kirbybase import KirbyBase

# db = KirbyBase(imgdb, fast=True)

# askquestions = settings['askquestions']
# normname = settings['normname']
# allnormsources = settings['normsources']
# setnames = settings['setnames']
# decnormfieldname = settings['decnormfieldname']
# workdir = settings['workdir']



# seeinglimit = 0.9
# print(f"We are going to stack all images with seeing below {seeinglimit}...")


# refimgname_per_band = settings['refimgname_per_band']


# for setname in setnames:
#     refimgname = refimgname_per_band[setname]


#     bandimages = db.select(imgdb, ['gogogo', 'treatme', 'setname', 'seeing'], 
#                              [True, True, setname, f'<{seeinglimit}'], 
#                              returnType='dict', 
#                              sortFields=['mhjd'])
#     print(f" ... in the {setname} band, that is {len(bandimages)} images.")
#     imgnorms = []
#     for im in bandimages:
#         imgpath = os.path.join(alidir, im['imgname'] + '_ali.fits')
#         imgnorms.append(im[decnormfieldname] * fits.getdata(imgpath))
#     stack = np.nanmedian(imgnorms, axis=0)
#     fits.writeto(os.path.join(workdir, f'{setname}_stack.fits'), stack, overwrite=1)


