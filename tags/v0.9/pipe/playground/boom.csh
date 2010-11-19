cd 1_character_scripts/
	python 1_header_pyfits.py
	python 2_seeing.py
	python 3_hjd.py
cd ../

cd 2_reduc_scripts/
	python 1_skysub.py
	#python 1alt_noskysub.py
cd ../

cd 3_align_scripts/
	python 1_identcoord.py
	python 2_alignimages.py
	python 3_hjd.py
cd ../

cd 4_norm_scripts/
	python 1_imstat.py
	python 2_runsex.py
	python 3_calccoeff.py
cd ../

cd 5_psf_scripts/
	python 1_extract.py
	python 1a_replacenan.py
	python 2_psf.py
cd ../

cd 6_deconv_scripts/
	python 1_prepfiles.py
	python 2_applynorm.py
	python 3_fillinfile.py
	python 4_deconv.py
	python 5_readout.py
cd ../



#cd 9_various_scripts/
#python 1_smalllens_mov.py
#python 2_fullframe_mov.py
#cd ../

