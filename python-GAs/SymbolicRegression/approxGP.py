# Bizzaro Francesco
# March 2020
#
# This script keeps executing a Genetic algorithm
# to solve a Symbolic Regression problem instance.
# It is executed by a set of miners, for 100 generations,
# from a previous state.

import random
import operator
import numpy
import math
import sys
import json

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

# symbolic regression
import os.path
xrange = range
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NAME = sys.argv[1]
tp = str(sys.argv[2])
repetition = 0
FOLDER_POP = NAME+"/pop_"+str(repetition)
FOLDER_POPPREV = NAME+"/pop_"+str(repetition-1)
FOLDER_RES = NAME+"/results"
MAXTERMS = 40

inputs = []
outputs = []
filepath = BASE_DIR + '/problems/' + str(tp) + '/' + NAME + '.json'
with open(filepath, "r") as knap_data:
    probl = json.load(knap_data)
    inputs = probl["x"]
    outputs = probl["y"]

assert(len(inputs)==len(outputs))

POP = 300
OFFSPR = 150
GEN = 100
MNRS = 100
print(tp,repetition,":")
random.seed(repetition)

def mydiv(x,y):
    if y==0:
        return 1
    return float(x)/float(y)

# define the available operators and terminals
pset = gp.PrimitiveSet("MAIN", 1, "X")
pset.addPrimitive(math.sin, 1)
pset.addPrimitive(math.cos, 1)
pset.addPrimitive(mydiv, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.neg, 1)
pset.addTerminal(1.0)
pset.addTerminal(0.0)
# pset.addEphemeralConstant("rand101", lambda: random.randint(-1,1))

best_raw = []
best_scored = []
if repetition>0 and tp=="Coop":
    print("import best shared solutions")
    with open(FOLDER_RES+"/"+tp+str(repetition-1)+".txt","r") as f:
        rawlist = []
        for row in f.readlines():
            ids = int(row[:row.find(",")])
            row = row[row.find(",")+1:]
            eval = float(row[:row.find(",")])
            row = row[row.find(",")+1:]
            sol = row[row.find(",")+1:]
            # print sol
            rawlist.append({
                "id":ids,
                "eval":eval,
                "sol":sol
            })
        rawlist.sort(key=lambda x: x["eval"], reverse=False)
        best_raw.append(rawlist[0])
        if float(best_raw[0]["eval"])!=0.0:
            for i in range(50):
                s = rawlist[i]
                print(s["id"],s["eval"])#,s["sol"][0],len(s["sol"])
                sol = s["sol"]
                best_scored.append(gp.PrimitiveTree.from_string(sol,pset))


evalIDs = ["-1"]
evalToolbox = [None]
def eval(individual):
    if len(individual)>MAXTERMS:
        return 9e+30,
    try:
        func = getattr(evalToolbox[0],"compile"+evalIDs[0])(expr=individual)
        ev = 0
        N = len(inputs)
        coeff = 1.0/float(N)
        for i in range(N):
            x = inputs[i]
            y = outputs[i]
            ev += coeff*math.pow(func(x)-y,2)
        return ev,#(1+ev)*(100+len(individual)),
    except Exception as e:
        return 9e+30,


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
    return [gp.PrimitiveTree.from_string(s,pset) for s in pop]

def savePopulation(population,pid):
    # print population[0]
    with open(FOLDER_POP+"/"+tp+str(repetition)+"_"+pid+".json", 'w') as outfile:
        json.dump([str(i) for i in population], outfile)

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
    creator.create("Fitness"+ids, base.Fitness, weights=(-1.0,))
    creator.create("Individual"+ids, gp.PrimitiveTree,
        fitness=getattr(creator,"Fitness"+ids))
    toolbox = base.Toolbox()
    toolbox.register("expr"+ids, gp.genFull, pset=pset, min_=3, max_=5)
    toolbox.register("individual"+ids, tools.initIterate,
        getattr(creator,"Individual"+ids), getattr(toolbox,"expr"+ids))
    if repetition==0:
        toolbox.register("population"+ids, tools.initRepeat, list,
            getattr(toolbox,"individual"+ids))
    else:
        curID[0] = ids
        toolbox.register("population"+ids,load_individuals,
            getattr(creator,"Individual"+ids))
    toolbox.register("compile"+ids, gp.compile, pset=pset)
    toolbox.register("evaluate"+ids, eval)
    toolbox.register("select"+ids, tools.selTournament, tournsize=5)
    toolbox.register("mate"+ids, gp.cxOnePoint)
    toolbox.register("expr_mut"+ids, gp.genGrow, min_=0, max_=2)
    toolbox.register("mutate"+ids, gp.mutUniform,
        expr=getattr(toolbox,"expr_mut"+ids), pset=pset)
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



def opToString(op):
    if op=="add":
        return " + "
    if op=="neg" or op=="sub":
        return " - "
    if op=="mul":
        return " * "
    if op=="mydiv":
        return " / "
    if op=="mypow":
        return "^"
    return op

def varToString(v):
    if v=="X0":
        return "x"
    return v

def solTree(sol,i):
    name = sol[i].name
    arity = sol[i].arity
    if arity==0:
        return 1,varToString(name)
    args = ""
    ind = i+1
    for a in range(arity):
        off,arg = solTree(sol,ind)
        args += arg+","
        ind += off
    if arity==1:
        return ind-i,opToString(name)+"("+args[:-1]+")"
    return ind-i,"("+(args[:-1]).replace(",",opToString(name))+")"

def solToString(sol):
    return solTree(sol,0)[1]


def startSearcher(ids):
    toolbox = initGA(str(ids))
    evalIDs[0] = str(ids)
    evalToolbox[0] = toolbox
    pop = getattr(toolbox,"population"+str(ids))(n=POP)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", numpy.min)
    pop2,_ = MyeaMuPlusLambda(str(ids),pop,toolbox,OFFSPR,
           OFFSPR,0.7,0.2,GEN,stats=stats,halloffame=hof,verbose=False)
    savePopulation(pop2,str(ids))

    parz = str(hof[0])
    # print parz

    parz = parz[parz.find("(")+1:parz.rfind(")")]
    with open(FOLDER_RES+"/"+tp+str(repetition)+".txt", "a+") as f:
        f.write(str(ids)+","+str(hof[0].fitness.values[0])
            +","+parz+")\n")
    return ids,hof[0].fitness.values

def main():

    if len(best_raw)>0:
        if float(best_raw[0]["eval"])==0.0:
            for i in range(MNRS):
                ids = i
                with open(FOLDER_RES+"/"+tp+str(repetition)+".txt", "a+") as f:
                    f.write(str(ids)+","+str(0.0)+",-\n")
            return 0
    best = 9e+31

    bestown = -1
    for i in range(MNRS):
        own,sol = startSearcher(i)
        if(sol[0]<best):
            best = sol[0]
            bestown = own
        print("current best:",best,"[from ",bestown,"]","[",tp,NAME,repetition,"]")

if __name__ == "__main__":
    main()
