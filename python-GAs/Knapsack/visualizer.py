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

best_of_all = -1

# problems = [
#     "knap0_120","knap1_129","knap2_60"
#     ,"knap3_40","knap4_65","knap5_42","knap6_132"
#     ,"knap7_87","knap8_69","knap9_88"]

# problems = [
#     "knap0_805","knap1_622","knap2_466"
#     ,"knap3_194","knap4_534","knap5_621","knap6_253"
#     ,"knap7_198","knap8_996","knap9_200"]

# problems = [
#     "2/knap0_2594","2/knap1_2334","2/knap2_1555"
#     ,"2/knap3_2829","2/knap4_2883","2/knap5_1272","2/knap6_1131"
#     ,"2/knap7_1019","2/knap8_2391","2/knap9_2357"]

problems = [
    "0/knap0_120","0/knap1_129","0/knap2_60"
    ,"0/knap3_40","0/knap4_65","0/knap5_42","0/knap6_132"
    ,"0/knap7_87","0/knap8_69","0/knap9_88"
    ,"1/knap0_805","1/knap1_622","1/knap2_466"
    ,"1/knap3_194","1/knap4_534","1/knap5_621","1/knap6_253"
    ,"1/knap7_198","1/knap8_996","1/knap9_200"
    ,"2/knap0_2594","2/knap1_2334","2/knap2_1555"
    ,"2/knap3_2829","2/knap4_2883","2/knap5_1272","2/knap6_1131"
    ,"2/knap7_1019","2/knap8_2391","2/knap9_2357"
    ]

for p in range(len(problems)):
    prb = problems[p]
    sing_best = []
    sing_avg = []
    coop_best = []
    coop_avg = []
    best_of_all = -1
    for i in range(5):
        path_sing = "problems/"+prb+"/results/Sing"+str(i)+".txt"
        path_coop = "problems/"+prb+"/results/Coop"+str(i)+".txt"
        with open(path_sing,"r") as fsing:
            best = -1.0
            avg = 0.0
            tot = 0.0
            for line in fsing.readlines():
                tot += 1.0
                cur = float(line.split(",")[1])
                avg += cur
                if(cur>best):
                    best = cur
                if cur>best_of_all:
                    best_of_all = cur
            avg = float(avg)/float(tot)
            sing_best.append(best)
            sing_avg.append(avg)
        with open(path_coop,"r") as fsing:
            best = -1.0
            avg = 0.0
            tot = 0.0
            for line in fsing.readlines():
                tot += 1.0
                cur = float(line.split(",")[1])
                avg += cur
                if(cur>best):
                    best = cur
                if cur>best_of_all:
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
plt.legend(bbox_to_anchor=(1,0),loc=4,borderaxespad=0.,frameon=False)
plt.tight_layout()
plt.savefig("knapsack_tot.png")
plt.show()

print "coop best:",mean_coop_best[len(mean_coop_best)-1]/float(len(problems))
print "sing best:",mean_sing_best[len(mean_coop_best)-1]/float(len(problems))
