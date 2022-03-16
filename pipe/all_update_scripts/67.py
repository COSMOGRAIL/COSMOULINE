import os, sys
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))


os.system(f"{python} 6_extract.py")
os.system(f"{python} 7_deconv.py")