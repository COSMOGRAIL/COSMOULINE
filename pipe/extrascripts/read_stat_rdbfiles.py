import numpy as np
import pickle as pkl
import pycs, os
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['xtick.labelsize'] = 14
mpl.rcParams['ytick.labelsize'] = 14

rdb_list = [
     "/Users/martin/Desktop/cosmograil-dr1/WFI_lenses/HE0047_WFI/HE0047_WFI.rdb",
     "/Users/martin/Desktop/cosmograil-dr1/WFI_lenses/WG0214_WFI/WG0214_WFI.rdb",
     "/Users/martin/Desktop/cosmograil-dr1/WFI_lenses/DES0407_WFI/DES0407_WFI.rdb",
     "/Users/martin/Desktop/cosmograil-dr1/WFI_lenses/J0832_WFI/J0832_WFI.rdb",
     "/Users/martin/Desktop/cosmograil-dr1/WFI_lenses/2M1134_WFI/2M1134_WFI.rdb",
     "/Users/martin/Desktop/cosmograil-dr1/WFI_lenses/PS1606_WFI/PS1606_WFI.rdb",
]

object_list = [os.path.basename(r).split("_")[0] for  r in rdb_list]
print object_list
nicename = [
 ' HE 0047-1756',
 ' WG 0214-2105',
 ' DES 0407-5006',
 ' SDSS J0832+0404',
 ' 2M 1134-2103',
 ' PSJ 1606-2333',
]

mycolours = ["darkorange", "royalblue", "seagreen", "purple", "brown", "magenta", "orange"]
fig1 = plt.figure(figsize=(12,8))
ax1 = fig1.add_subplot(1,2,1)
ax2 = fig1.add_subplot(1,2,2)
plt.subplots_adjust(left = 0.1, right=0.98, top=0.96, bottom=0.1, wspace=0.08, hspace=0.0)

handle_list = []
for i,rdb in enumerate(rdb_list):

     lc = pycs.gen.lc.rdbimport(rdb_list[i], object='A', magcolname="mag_A", magerrcolname="magerr_A_5", mhjdcolname="mhjd", flagcolname = None, propertycolnames = "lcmanip", verbose = False)

     seeings = [float(prop['fwhm']) for prop in lc.properties]
     airmass = [float(prop['airmass']) for prop in lc.properties]
     skylevel = [float(prop['relskylevel']) for prop in lc.properties]
     nbimage = [float(prop['nbimg']) for prop in lc.properties]
     ellipticity = [float(prop['ellipticity']) for prop in lc.properties]

     print  "### %s ### "% object_list[i]
     print "Epochs : ", len(lc.jds)
     print "Median seeing : ", np.median(seeings)
     print "Median airmass : ", np.median(airmass)
     print "Median skylevel : ", np.median(skylevel)
     print "Median nbimage : ", np.median(nbimage)
     print "Median ellipticity : ", np.median(ellipticity)


     ax1.hist(seeings, histtype= 'step', color= mycolours[i], label=nicename[i], density= True, linewidth = 2)
     ax2.hist(airmass, histtype= 'step', color= mycolours[i], label=nicename[i], density= True, linewidth = 2)

# Create new legend handles but use the colors from the existing ones
handles, labels = ax1.get_legend_handles_labels()
new_handles = [mpl.lines.Line2D([], [], c=h.get_edgecolor()) for h in handles]

ax1.set_xlabel('Seeing (per epoch) ["]', fontdict={"fontsize": 20})
ax2.set_xlabel('Airmass (per epoch)', fontdict={"fontsize": 20})
ax1.set_ylabel('Normalised distribution', fontdict={"fontsize": 20})
ax1.legend(handles=new_handles, labels = labels, fontsize = 16)

name = "/Users/martin/Desktop/DR2/paperplot/seeing.pdf"
fig1.savefig("/Users/martin/Desktop/DR2/paperplot/seeing.pdf")
os.system("pdfcrop %s %s"%(name,name))

plt.show()

