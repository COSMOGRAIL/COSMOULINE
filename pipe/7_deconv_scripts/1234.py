import os

#os.system("python 0_facult_autoskiplist_NU.py")
os.system("python3 1_prepfiles.py")
os.system("python3 2_applynorm_NU.py")
os.system("python3 3_fillinfile_NU.py")
#os.system("cp  ../../data/WFI2033_SMARTS/back2.fits ../../data/WFI2033_SMARTS/dec_back_lens_renormdfkmn_pyMCSacegr/back2.fits")
os.system("python3 4_deconv_NU.py")
os.system("python3 5b_showptsrc_NU.py")
os.system("python3 5a_decpngcheck_NU.py")
