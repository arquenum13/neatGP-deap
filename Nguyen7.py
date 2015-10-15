import operator
import math
import random
import csv
import numpy
from decimal import Decimal
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp
from neat_operators import neatGP
from ParentSelection import sort_fitnessvalues


def safe_div(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 0


def mylog(x):
    if x==0:
        return 0
    else:
        return math.log10(abs(x))


def mysqrt(x):
    if x<=0:
        return 0
    else:
        return math.sqrt(x)


def mypower2(x):
    y=math.pow(x,2)
    if isinstance(y,complex) or math.isinf(y) or math.isnan(y):
        return 0
    else:
        return y


def mypower3(x):
    y=math.pow(x,3)
    if isinstance(y,complex) or math.isinf(y) or math.isnan(y):
        return 0
    else:
        return y


pset = gp.PrimitiveSet("MAIN", 1)
pset.addPrimitive(operator.add, 2)  # Koza, Korns
pset.addPrimitive(operator.sub, 2)  # Koza, Korns
pset.addPrimitive(operator.mul, 2)  # Koza, Korns
pset.addPrimitive(safe_div, 2)  # Koza, Korns
pset.addPrimitive(math.cos, 1)  # Koza, Korns
pset.addPrimitive(math.sin, 1)  # Koza, Korns
#pset.addPrimitive(math.exp,1)  # Koza Korns
pset.addPrimitive(mylog,1)  # Koza, Korns
pset.addPrimitive(math.tan, 1)  # Koza, Korns
pset.addPrimitive(math.tanh, 1)  # Koza, Korns
pset.renameArguments(ARG0='x')  # Koza

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("FitnessTest", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin, fitness_test=creator.FitnessTest)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genFull, pset=pset, min_=1, max_=3)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)


def evalSymbReg(individual, points):
    func = toolbox.compile(expr=individual)
    sqerrors = ((func(x) - (math.log(x+1.0)+math.log(x**2+1.0)))**2 for x in points)
    return math.fsum(sqerrors) / len(points),


def Nguyen7(n_corr):
    with open("./data_corridas/Nguyen7/corrida%d/test_x.txt" %n_corr) as spambase:
        spamReader = csv.reader(spambase)
        spam = [float(row[0]) for row in spamReader]
    with open("./data_corridas/Nguyen7/corrida%d/train_x.txt"%n_corr) as spamb:
        spamReader2 = csv.reader(spamb)
        spam2 = [float(row[0]) for row in spamReader2]
    toolbox.register("evaluate", evalSymbReg, points=spam2)
    toolbox.register("evaluate_test", evalSymbReg, points=spam)


def main(n_corr, p):
    Nguyen7(n_corr)

    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=3)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

    pop = toolbox.population(n=500)
    hof = tools.HallOfFame(3)

    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    stats_fit_test=tools.Statistics(lambda i: i.fitness_test.values)
    mstats = tools.MultiStatistics(fitness=stats_fit,size=stats_size, fitness_test= stats_fit_test)
    mstats.register("avg", numpy.mean)
    mstats.register("std", numpy.std)
    mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)
    params = ['best_of_each_specie', 2, 'yes']
    neatcx = True
    alg = True
    pelit = 0.6
    pop, log = algorithms.eaSimple(pop, toolbox, 0.7, 0.3, 100, alg, neatcx, 0.15, pelit, n_corr, p, params, stats=mstats, halloffame=hof, verbose=True)

    outfile = open('popfinal_%d_%d.txt'%(p,n_corr), 'w')

    outfile.write("\n Best individual is: %s %s %s " % (str(hof[0]), hof[0].fitness, hof[0].fitness_test))
    outfile.write("\n Best individual is: %s %s %s" % (str(hof[1]), hof[1].fitness, hof[1].fitness_test))
    outfile.write("\n Best individual is: %s %s %s" % (str(hof[2]), hof[2].fitness, hof[2].fitness_test))

    sortf = sort_fitnessvalues(pop)
    for ind in sortf:
        outfile.write("\n ind: %s %s %s " % (ind.fitness.values, ind.get_fsharing(), ind))

    outfile.close()
    return pop, log, hof


def run(number, problem):
    n = 1
    while n <= number:
        main(n, problem)
        n += 1


if __name__ == "__main__":
    n = 1
    while n < 3:
        main(n)
        n += 1