# Bizzaro Francesco
# March 2020
#
# This script keeps executing a Genetic algorithm
# to solve a TSP problem instance.
# It is executed by a set of miners, for 100 generations,
# from a previous state.

import array
import random
import json
import sys
import threading
import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

NAME = sys.argv[1]
tp = str(sys.argv[2])
repetition = int(sys.argv[3])
FOLDER_POP = NAME+"/pop_"+str(repetition)
FOLDER_POPPREV = NAME+"/pop_"+str(repetition-1)
FOLDER_RES = NAME+"/results"

with open(NAME+".json", "r") as tsp_data:
    tsp = json.load(tsp_data)

distance_map = tsp["DistanceMatrix"]
IND_SIZE = tsp["TourSize"]
POP = 600
OFFSPR = 300
GEN = 100
MNRS = 100
print tp,repetition,":"
# repetition = 6
# tp = "Sing"# Sing o Coop
random.seed(repetition)


best_scored = []
if repetition>0 and tp=="Coop":
    print "import best shared solutions"
    with open(FOLDER_RES+"/"+tp+str(repetition-1)+".txt","r") as f:
        rawlist = []
        for row in f.readlines():
            ids = int(row[:row.find(",")])
            row = row[row.find(",")+1:]
            eval = float(row[:row.find(",")])
            sol = row[row.find("[")+1:row.rfind("]")]
            rawlist.append({
                "id":ids,
                "eval":eval,
                "sol":sol.split(", ")
            })
        rawlist.sort(key=lambda x: x["eval"], reverse=False)
        for i in range(50):
            s = rawlist[i]
            print s["id"],s["eval"],s["sol"][0],len(s["sol"])
            best_scored.append([int(x) for x in s["sol"]])

def evalTSP(individual):
    distance = distance_map[individual[-1]][individual[0]]
    for gene1, gene2 in zip(individual[0:-1], individual[1:]):
        distance += distance_map[gene1][gene2]
    return distance,

def load_shared_individuals(creator,n):
    individuals = []
    for i in range(len(best_scored)):
        individual = best_scored[i]
        individual = creator(individual)
        individuals.append(individual)
    return individuals

def loadLastPopulation(pid):
    pop = []
    with open(FOLDER_POPPREV+"/"+tp+str(repetition-1)+"_"+pid+".json", "r") as f:
        pop = json.load(f)
    return pop

def savePopulation(population,pid):
    with open(FOLDER_POP+"/"+tp+str(repetition)+"_"+pid+".json", 'w') as outfile:
        json.dump([[g for g in i] for i in population], outfile)

curID = ["-1"]
def load_individuals(creator,n):
    individuals = []
    lastPop = loadLastPopulation(curID[0])
    for i in range(len(lastPop)):
        individual = lastPop[i]
        individual = creator(individual)
        individuals.append(individual)
    return individuals

def initGA(ids):
    creator.create("FitnessMin"+ids, base.Fitness, weights=(-1.0,))
    creator.create("Individual"+ids, array.array, typecode='i', fitness=getattr(creator,"FitnessMin"+ids))
    toolbox = base.Toolbox()
    # Attribute generator
    toolbox.register("indices"+ids, random.sample, range(IND_SIZE), IND_SIZE)
    # Structure initializers
    toolbox.register("individual"+ids, tools.initIterate,
        getattr(creator,"Individual"+ids), getattr(toolbox,"indices"+ids))
    if repetition==0:
        toolbox.register("population"+ids, tools.initRepeat, list,
            getattr(toolbox,"individual"+ids))
    else:
        curID[0] = ids
        toolbox.register("population"+ids,load_individuals,
            getattr(creator,"Individual"+ids))
    toolbox.register("mate"+ids, tools.cxPartialyMatched)
    toolbox.register("mutate"+ids, tools.mutShuffleIndexes, indpb=0.005)
    toolbox.register("select"+ids, tools.selTournament, tournsize=80)
    toolbox.register("evaluate"+ids, evalTSP)
    if repetition>0 and tp=="Coop":
        toolbox.register("populationC"+ids,load_shared_individuals,
            getattr(creator,"Individual"+ids))
    return toolbox


def MyvarOr(ids,population, toolbox, lambda_, cxpb, mutpb):
    assert (cxpb + mutpb) <= 1.0, (
        "The sum of the crossover and mutation probabilities must be smaller "
        "or equal to 1.0.")
    offspring = []
    for _ in xrange(lambda_):
        op_choice = random.random()
        if op_choice < cxpb:            # Apply crossover
            ind1, ind2 = map(toolbox.clone, random.sample(population, 2))
            ind1, ind2 = getattr(toolbox,"mate"+ids)(ind1, ind2)
            del ind1.fitness.values
            offspring.append(ind1)
        elif op_choice < cxpb + mutpb:  # Apply mutation
            ind = toolbox.clone(random.choice(population))
            ind, = getattr(toolbox,"mutate"+ids)(ind)
            del ind.fitness.values
            offspring.append(ind)
        else:                           # Apply reproduction
            offspring.append(random.choice(population))

    return offspring

def MyeaMuPlusLambda(ids,population, toolbox, mu, lambda_, cxpb, mutpb, ngen,
                   stats=None, halloffame=None, verbose=__debug__):
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])
    if repetition>0 and tp=="Coop":
        popC = getattr(toolbox,"populationC"+ids)(n=len(best_scored))
        population += popC
    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(getattr(toolbox,"evaluate"+ids), invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    if halloffame is not None:
        halloffame.update(population)
    record = stats.compile(population) if stats is not None else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print logbook.stream
    # Begin the generational process
    for gen in range(1, ngen + 1):
        # Vary the population
        offspring = MyvarOr(ids,population, toolbox, lambda_, cxpb, mutpb)
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(getattr(toolbox,"evaluate"+ids), invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)
        # Select the next generation population
        population[:] = getattr(toolbox,"select"+ids)(population + offspring, mu)
        # Update the statistics with the new population
        record = stats.compile(population) if stats is not None else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print logbook.stream
    return population, logbook


def startSearcher(ids):
    toolbox = initGA(str(ids))
    pop = getattr(toolbox,"population"+str(ids))(n=POP)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", numpy.min)
    pop2,_ = MyeaMuPlusLambda(str(ids),pop,toolbox,OFFSPR,
           OFFSPR,0.7,0.2,GEN,stats=stats,halloffame=hof,verbose=False)
    #return pop, stats, hof
    savePopulation(pop2,str(ids))
    print len(pop2)
    print ids,",",hof[0].fitness.values[0]
    with open(FOLDER_RES+"/"+tp+str(repetition)+".txt", "a+") as f:
        f.write(str(ids)+","+str(hof[0].fitness.values[0])
            +","+str(hof[0].tolist())+"\n")
    return ids,hof[0].fitness.values[0]

if __name__ == "__main__":
    # print sys.argv[1]
    best = 99999999999999
    bestown = -1
    for i in range(MNRS):
        own,sol = startSearcher(i)
        if(sol<best):
            best = sol
            bestown = own
        print "current best:",best,"[from ",bestown,"]","[",tp,repetition,"]"
