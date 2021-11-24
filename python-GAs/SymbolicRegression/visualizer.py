# Bizzaro Francesco
# March 2020
#
# This script can be used to plot
# the results of all the GAs executed.

from matplotlib import pyplot as plt
import json
import datetime
import numpy as np
from math import exp, pow
from operator import add

mean_sing_best = []
mean_sing_avg = []
mean_coop_best = []
mean_coop_avg = []

best_of_all = 99999999999999

problems = [
    "0/approx0", "0/approx1", "0/approx2"
    , "0/approx3", "1/approx4", "1/approx5"]

for p in range(len(problems)):
    prb = problems[p]
    sing_best = []
    sing_avg = []
    coop_best = []
    coop_avg = []
    best_of_all = 99999999999999
    for i in range(5):
        path_sing = "./" + prb + "/results/Sing" + str(i) + ".txt"
        path_coop = "./" + prb + "/results/Coop" + str(i) + ".txt"
        with open(path_sing, "r") as fsing:
            best = 99999999999999
            avg = 0.0
            tot = 0.0
            for line in fsing.readlines():
                tot += 1.0
                cur = float(line.split(",")[1])
                avg += cur
                if (cur < best):
                    best = cur
                if cur < best_of_all:
                    best_of_all = cur
            avg = float(avg) / float(tot)
            sing_best.append(best)
            sing_avg.append(avg)
        with open(path_coop, "r") as fsing:
            best = 99999999999999
            avg = 0.0
            tot = 0.0
            for line in fsing.readlines():
                tot += 1.0
                cur = float(line.split(",")[1])
                avg += cur
                if (cur < best):
                    best = cur
                if cur < best_of_all:
                    best_of_all = cur
            avg = float(avg) / float(tot)
            coop_best.append(best)
            coop_avg.append(avg)
    best_of_all = 1.0
    if p == 0:
        mean_sing_best = [float(y) / float(best_of_all) for y in sing_best]
        mean_sing_avg = [float(y) / float(best_of_all) for y in sing_avg]
        mean_coop_best = [float(y) / float(best_of_all) for y in coop_best]
        mean_coop_avg = [float(y) / float(best_of_all) for y in coop_avg]
    else:
        mean_sing_best = list(map(add, mean_sing_best,
                                  [float(y) / float(best_of_all) for y in sing_best]))
        mean_sing_avg = list(map(add, mean_sing_avg,
                                 [float(y) / float(best_of_all) for y in sing_avg]))
        mean_coop_best = list(map(add, mean_coop_best,
                                  [float(y) / float(best_of_all) for y in coop_best]))
        mean_coop_avg = list(map(add, mean_coop_avg,
                                 [float(y) / float(best_of_all) for y in coop_avg]))

plt.plot([100 * x for x in range(1, 1 + (len(mean_sing_best)))],
         [y / float(len(problems)) for y in mean_sing_best], label="Std best",
         linestyle=":", color="k", linewidth=2)
plt.plot([100 * x for x in range(1, 1 + (len(mean_sing_best)))],
         [y / float(len(problems)) for y in mean_sing_avg], label="Std avg",
         linestyle="-.", color="k", linewidth=2)
plt.plot([100 * x for x in range(1, 1 + (len(mean_sing_best)))],
         [y / float(len(problems)) for y in mean_coop_best], label="Coop best",
         linestyle="-", color="k", linewidth=2)
plt.plot([100 * x for x in range(1, 1 + (len(mean_sing_best)))],
         [y / float(len(problems)) for y in mean_coop_avg], label="Coop avg",
         linestyle="--", color="k", linewidth=2)
plt.xlabel("Generations")
plt.ylabel("Mean Squared Error")
plt.legend(bbox_to_anchor=(1, 0.5), loc=1, borderaxespad=0., frameon=False)
plt.tight_layout()
plt.savefig("approx.png")
plt.show()

print("coop best:", mean_coop_avg[len(mean_coop_best) - 1] / float(len(problems)))
print("sing best:", mean_sing_avg[len(mean_coop_best) - 1] / float(len(problems)))
