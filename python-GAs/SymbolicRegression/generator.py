# Bizzaro Francesco
# March 2020
#
# This script can generate random
# Symbolic Regression problem instances.

import random
import json
import math
import numpy as np

def f1(x):
    return 3+1/(x+1)+math.pow(x,2)

def f2(x):
    return x*math.sin(3*x)

def f3(x):
    return math.cos(math.sin(x))+0.5*x

def f4(x):
    return 3-2*x+math.pow(x,3)

def f5(x):
    return math.atan(x)

def f6(x):
    return math.pi

def f7(x):
    return math.sqrt(x)

def f8(x):
    return (11.0/7.0)*x

fs = [f1,f2,f3,f4,f5,f6]
for i in range(len(fs)):
    fun = fs[i]
    x = [xx for xx in np.arange(0,20,0.5)]
    y = [fun(xx) for xx in x]
    p = {"x":x,"y":y}
    with open("problems/approx"+str(i)+".json","w") as f:
        json.dump(p,f)
print("done!")
