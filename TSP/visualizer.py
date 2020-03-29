# Bizzaro Francesco
# March 2020
#
# This script can be used to plot
# the results of all the GAs executed.

from matplotlib import pyplot as plt
import json
import datetime
import numpy as np
from math import exp,pow
from operator import add

mean_sing_best = []
mean_sing_avg = []
mean_coop_best = []
mean_coop_avg = []

best_of_all = 99999999999999

problems = [
    "0/burma14","0/gr96","0/pr76"
    ,"0/rat99","0/st70",
    "1/bier127","1/ch130","1/ch150"
    ,"1/d198","1/eil101","1/gr137","1/gr202"
    ,"1/kroA100","1/kroA150","1/kroA200","1/kroB100"
    ,"1/kroB150","1/kroB200","1/kroC100","1/kroD100"
    ,"1/kroE100","1/lin105","1/pr107","1/pr124"
    ,"1/pr136","1/pr144","1/pr152","1/rat195"
    ,"1/rd100","1/u159",
    "2/a280","2/ali535","2/d493"
    ,"2/d657","2/fl417","2/gr229","2/gr431"
    ,"2/gr666","2/lin318","2/p654","2/pcb442"
    ,"2/pr226","2/pr264","2/pr299","2/pr439"
    ,"2/rat575","2/rat783","2/rd400","2/ts225"
    ,"2/tsp225","2/u574","2/u724",
    "res3/d1291","res3/d1655","res3/fl1577"
    ,"res3/nrw1379","res3/pcb1173","res3/pr1002","res3/rl1304"
    ,"res3/rl1323","res3/u1060","res3/u1432","res3/u1817"
    ,"res3/vm1084","res3/vm1748"]


for p in range(len(problems)):
    prb = problems[p]
    sing_best = []
    sing_avg = []
    coop_best = []
    coop_avg = []
    best_of_all = 99999999999999
    for i in range(5):
        path_sing = "./"+prb+"/results/Sing"+str(i)+".txt"
        path_coop = "./"+prb+"/results/Coop"+str(i)+".txt"
        with open(path_sing,"r") as fsing:
            best = 99999999999999
            avg = 0.0
            tot = 0.0
            for line in fsing.readlines():
                tot += 1.0
                cur = float(line.split(",")[1])
                avg += cur
                if(cur<best):
                    best = cur
                if cur<best_of_all:
                    best_of_all = cur
            avg = float(avg)/float(tot)
            sing_best.append(best)
            sing_avg.append(avg)
        with open(path_coop,"r") as fsing:
            best = 99999999999999
            avg = 0.0
            tot = 0.0
            for line in fsing.readlines():
                tot += 1.0
                cur = float(line.split(",")[1])
                avg += cur
                if(cur<best):
                    best = cur
                if cur<best_of_all:
                    best_of_all = cur
            avg = float(avg)/float(tot)
            coop_best.append(best)
            coop_avg.append(avg)
    if p==0:
        mean_sing_best = [float(y)/float(best_of_all) for y in sing_best]
        mean_sing_avg = [float(y)/float(best_of_all) for y in sing_avg]
        mean_coop_best = [float(y)/float(best_of_all) for y in coop_best]
        mean_coop_avg = [float(y)/float(best_of_all) for y in coop_avg]
    else:
        mean_sing_best = list(map(add,mean_sing_best,
            [float(y)/float(best_of_all) for y in sing_best]))
        mean_sing_avg = list(map(add,mean_sing_avg,
            [float(y)/float(best_of_all) for y in sing_avg]))
        mean_coop_best = list(map(add,mean_coop_best,
            [float(y)/float(best_of_all) for y in coop_best]))
        mean_coop_avg = list(map(add,mean_coop_avg,
            [float(y)/float(best_of_all) for y in coop_avg]))

plt.plot([100*x for x in range(1,1+(len(mean_sing_best)))],
        [y/float(len(problems)) for y in mean_sing_best],label="Std best",
        linestyle=":",color="k",linewidth=2)
plt.plot([100*x for x in range(1,1+(len(mean_sing_best)))],
        [y/float(len(problems)) for y in mean_sing_avg],label="Std avg",
        linestyle="-.",color="k",linewidth=2)
plt.plot([100*x for x in range(1,1+(len(mean_sing_best)))],
        [y/float(len(problems)) for y in mean_coop_best],label="Coop best",
        linestyle="-",color="k",linewidth=2)
plt.plot([100*x for x in range(1,1+(len(mean_sing_best)))],
        [y/float(len(problems)) for y in mean_coop_avg],label="Coop avg",
        linestyle="--",color="k",linewidth=2)
plt.xlabel("Generations")
plt.ylabel("Normalized Fitness")
plt.legend(bbox_to_anchor=(1,1),loc=1,borderaxespad=0.,frameon=False)
plt.tight_layout()
plt.savefig("tsp_tot.png")
plt.show()

print "coop best:",mean_coop_best[len(mean_coop_best)-1]/float(len(problems))
print "sing best:",mean_sing_best[len(mean_coop_best)-1]/float(len(problems))
