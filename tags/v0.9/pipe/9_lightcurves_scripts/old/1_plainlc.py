#
#	plot a first simple lightcurve, to get the idea
#
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from pylab import * # matplotlib and NumPy etc

aname = "out_" + deckey + "A_int"
bname = "out_" + deckey + "B_int"

print aname, bname


db = KirbyBase()

data = db.select(imgdb, [deckeyfilenum], ['>0'], returnType='dict')
inta = asarray(map(lambda x:float(x[aname]), data))
intb = asarray(map(lambda x:float(x[bname]), data))
hjd = asarray(map(lambda x:float(x['mjd']), data))

seeing = asarray(map(lambda x:float(x['seeing']), data))

maga = -2.5 * log(inta)
magb = -2.5 * log(intb)

subplot(211)
plot(hjd, seeing, 'g.')
grid(True)
title(deckey, fontsize=20)

ylabel('Seeing [arcsec]')

subplot(212)
plot(hjd, maga, 'b.', hjd, magb, 'r.')
legend(('A', 'B'))
grid(True)

# reverse y axis for magnitudes :
ax=gca()
ax.set_ylim(ax.get_ylim()[::-1])

xlabel('MJD [days]')
ylabel('Magnitude')




show()
#savefig(workdir + "lc.png")




