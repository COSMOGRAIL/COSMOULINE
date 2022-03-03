
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from pylab import *
db = KirbyBase(imgdb)

data = db.select(imgdb, ['recno'], ['*'], ['seeing', 'geomaprms'])

x = [x[0] for x in data]
y = [x[1] for x in data]

#print data[0]
#title(r'$\alpha_i > \beta_i$', fontsize=20)
#plot(x,y, "r.")
#show()

title(r'$\alpha_i > \beta_i$', fontsize=20)
hist(x, 30)
savefig("bla.png")


