# Bizzaro Francesco
# March 2020
#
# This script keeps executing a Genetic algorithm
# to solve a Locomotion problem instance.
# It is executed by a set of miners, for 100 generations,
# from a previous state.

import random
import numpy
import sys
import json
import array

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import eval_motion as em


NAME = sys.argv[1]
tp = str(sys.argv[2])
repetition = int(sys.argv[3])
FOLDER_POP = NAME+"/pop_"+str(repetition)
FOLDER_POPPREV = NAME+"/pop_"+str(repetition-1)
FOLDER_RES = NAME+"/results"

NGEN = 10
MNRS = 10
MU = 12
LAMBDA = 25
CXPB = 0.6
MUTPB = 0.4
print(tp,repetition,":")
random.seed(repetition)

best_scored = []
if repetition>0 and tp=="Coop":
    print("import best shared solutions")
    with open(FOLDER_RES+"/"+tp+str(repetition-1)+".txt","r") as f:
        rawlist = []
        for row in f.readlines():
            ids = int(row[:row.find(",")])
            row = row[row.find(",")+1:]
            eval = float(row[:row.find(",")])
            sol = row[row.find("["):]
            rawlist.append({
                "id":ids,
                "eval":eval,
                "sol":json.loads(sol)
            })
        rawlist.sort(key=lambda x: x["eval"], reverse=True)
        for i in range(5):
            s = rawlist[i]
            print(s["id"],s["eval"],len(s["sol"]))
            best_scored.append(s["sol"])


def genMov():
    return [random.randint(0,20),
        random.uniform(-1,1),
        random.randint(1,999),
        random.randint(0,999)]

def evalLocomotion(individual):
    return em.simulateAndEval(em.parseMovements(individual),False),

def cxLocomotion(ind1, ind2):
    if random.random()<0.01 and ind1[0][2]>5 and ind2[0][2]>5:
        if random.random()<0.5:
            temp = ind1
            ind1 = ind2
            ind2 = temp
        for i in range(len(ind1)):
            ind1[i][2] *= 0.9
        return ind1,ind2
    tot = ind1+ind2
    random.shuffle(tot)
    j = 0
    for i in range(len(ind1)):
        ind1[i] = tot[j]
        j += 1
    for i in range(len(ind2)):
        ind2[i] = tot[j]
        j += 1
    return ind1, ind2

def mutLocomotion(individual):
    """Mutation that pops or add an element."""
    if random.random() < 0.5:
        if len(individual) > 0:
            del individual[random.randint(0,len(individual)-1)]
    else:
        individual.append(genMov())
    return individual,


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
        json.dump(population, outfile)

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
    creator.create("Fitness"+ids, base.Fitness, weights=(1.0,))
    creator.create("Individual"+ids, list,
        fitness=getattr(creator,"Fitness"+ids))
    toolbox = base.Toolbox()
    toolbox.register("attr_item"+ids, genMov)
    toolbox.register("individual"+ids, tools.initRepeat,
            getattr(creator,"Individual"+ids),
            getattr(toolbox,"attr_item"+ids), 30)
    if repetition==0:
        toolbox.register("population"+ids, tools.initRepeat, list,
            getattr(toolbox,"individual"+ids))
    else:
        curID[0] = ids
        toolbox.register("population"+ids,load_individuals,
            getattr(creator,"Individual"+ids))

    toolbox.register("evaluate"+ids, evalLocomotion)
    toolbox.register("mate"+ids, cxLocomotion)
    toolbox.register("mutate"+ids, mutLocomotion)
    toolbox.register("select"+ids, tools.selTournament,tournsize=10)

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
        print(logbook.stream)
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
            print(logbook.stream)
    return population, logbook


def startSearcher(ids):
    toolbox = initGA(str(ids))
    pop = getattr(toolbox,"population"+str(ids))(n=MU)
    hof = tools.HallOfFame(1)
    # hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", numpy.max)
    pop2,_ = MyeaMuPlusLambda(str(ids),pop,toolbox,MU,
           LAMBDA,CXPB,MUTPB,NGEN,stats=stats,halloffame=hof,verbose=True)
    savePopulation(pop2,str(ids))

    parz = json.dumps(hof[0])

    # parz = parz[parz.find("(")+1:parz.rfind(")")]
    with open(FOLDER_RES+"/"+tp+str(repetition)+".txt", "a+") as f:
        f.write(str(ids)+","+str(hof[0].fitness.values[0])
            +","+parz+"\n")
    return ids,hof[0].fitness.values

if __name__ == "__main__":
    best = -1
    bestown = -1
    for i in range(MNRS):
        own,sol = startSearcher(i)
        if(sol[0]>best):
            best = sol[0]
            bestown = own
        print("current best:",best,"[from ",bestown,"]","[",tp,NAME,repetition,"]")
