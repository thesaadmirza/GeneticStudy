# Bizzaro Francesco
# March 2020
#
# This script can generate random
# Knapsack problem instances.

import random
import json
import math

random.seed(566)

def gen_problem(n,limit,maxw=10,minw=1):
    probl = dict()
    probl["num_items"] = n
    probl["limit"] = limit
    items = {}
    for i in range(n):
        items[i] = (random.randint(minw, maxw), random.uniform(0,1.5*maxw))
    probl["items"] = items
    return probl

for i in range(10):
    n = random.randint(1000,3000)
    limit = random.randint(n/2,3*n)
    p = gen_problem(n,limit,max(100,math.ceil(0.2*limit+random.randint(1,10))),1)
    with open("problems/2/knap"+str(i)+"_"+str(n)+".json","w") as f:
        json.dump(p,f)
print("done!")
