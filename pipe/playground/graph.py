
execfile("../config.py")
from kirbybase import KirbyBase, KBError
from pylab import *
db = KirbyBase()

data = db.select(imgdb, ['recno'], ['*'], ['seeing', 'geomaprms'])

x = map(lambda x:x[0], data)
y = map(lambda x:x[1], data)

#print data[0]
#title(r'$\alpha_i > \beta_i$', fontsize=20)
#plot(x,y, "r.")
#show()

title(r'$\alpha_i > \beta_i$', fontsize=20)
hist(x, 30)
savefig("bla.png")


