

new :

Astro calculations, using pyephem.
The link from JD to HJD is explicitly calculated, no more black box stuff.
As a bonus, you get airmass, moonphase, Moon separation, sun altitude etc etc.

Much more rubust and precise seeing and ellipticity measure
Seeing measure done right.

Reliable cosmic ray rejection using cosmics.py, improving L.A.Cosmic

Sky level and noise estimations, before alignment, independent from sextractor.

Much better visualizations at all levels.

No more renormalization after deconvolutions, always before :

new concept of coeffcients :

medcoeff : with respect to one single ref frame

renorm : with respect to the median of the light curves of each star. Should be less problematic.

all these are saved "side by side" in the database, you can use them as you want for deconvolutions.
For a typical run, the aperture photometry is used only for guessing initialization values, and normalising the deconvolutions of some stars so that background objects are well treated.
From then on, you use renorm for the next deconvolutions.

for each deconvolutions, the name of the normalization you choose to use is immortalized in the deckey. It's very important to keep track of that, so that you can maken another renormalization using this deconvolution.

rdb export, ready for pycs !


lookback :
takes into account renormalisation , as it is simply based on the output of the deconvolution !




contents of this file were all transfered to the handbook ...


TODO :
	impose a uniform format of the "date" field
	make sure that jd and mjd are *both* for the center of the exposure !


Telescope specialities
-----------------------

Liverpool :
- no cropping, full 2048 x 2048 frame (for our cosmograil data), on other images there might be some binning !

Chandra :
- ugly borders. I cut the region [50:1999,50:1999]

