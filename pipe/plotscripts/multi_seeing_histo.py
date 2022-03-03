#
#    Histogramm of the measured seeings, for each set.
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
from pylab import * # matplotlib and NumPy etc

#imgdb = "/Users/mtewes/Desktop/vieuxdb.dat"

db = KirbyBase(imgdb)

# We read this only once.
images = db.select(imgdb, ['gogogo'], [True], returnType='dict')

usedsetnames = list(set([image['setname'] for image in images]))

nsets = len(usedsetnames)
figure(figsize=(6,1.4*nsets))    # set figure size

for i, name in enumerate(usedsetnames):

    # We extract the seeing values for this setname
    seeingvect = array([image['seeing'] for image in images if image['setname'] == name])
    print("%20s : %4i" %(name, len(seeingvect)))
    
    sub = 0.06+i*(0.88/nsets ) # relative position of the x axis on the figure.
    ax = axes([0.08, sub, 0.85, 0.78/nsets])
    
    # Write the setname on the graph
    ax.annotate(name, xy=(0.7, 0.7),  xycoords='axes fraction')
    
    if i > 0:    # hide labels
        ax.set_xticklabels([])
    else:
            xlabel("Seeing [arcsec]")

    n, bins, patches = hist(seeingvect, 100, range=(0.0,5.0), histtype='stepfilled', facecolor='grey')
    
    for tick in ax.yaxis.get_major_ticks(): # reduce the label fontsize.
        tick.label1.set_fontsize(8)

title('Seeing histogram', fontsize=18)
show()
    
