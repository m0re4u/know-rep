# @author: Petra Ormel, 2017
# @author: Michiel van der meer, 2017

from operator import itemgetter
import itertools
import json
import sys
import pycosat
import re
import time

with open('parsed.json') as data_file:
    data = json.load(data_file)

with open('solutions.json') as solution_file:
    soldata = json.load(solution_file)

sudokus = {}
for name in data:
    match = re.findall("\d+", name)[0]
    if match in soldata:
        sudokus[match] = {
            "solution": soldata[match],
            "data": data[name]
        }

print("Found {} sudoku/solution combinations!".format(len(sudokus)))

# constants
N = 9
M = 3
cnf = []


def exactly_one(variables):
    cnf = [variables]
    n = len(variables)

    for i in range(n):
        for j in range(i + 1, n):
            v1 = variables[i]
            v2 = variables[j]
            cnf.append([-v1, -v2])

    return cnf


def transform(i, j, k):
    return i * N * N + j * N + k + 1


def inverse_transform(v):
    v, k = divmod(v - 1, N)
    v, j = divmod(v, N)
    v, i = divmod(v, N)
    return i, j, k


def transformCell(cell):
    return cell[0] * N * N + cell[1] * N + cell[2] + 1


def makeCNF(constraints):
    cnf = []

    # Cell, row and column constraints
    for i in range(N):
        for s in range(N):
            cnf = cnf + exactly_one([transform(i, j, s) for j in range(N)])
            cnf = cnf + exactly_one([transform(j, i, s) for j in range(N)])

        for j in range(N):
            cnf = cnf + exactly_one([transform(i, j, k) for k in range(N)])

    # Sub-matrix constraints
    for k in range(N):
        for x in range(M):
            for y in range(M):
                v = [transform(y * M + i, x * M + j, k)
                     for i in range(M) for j in range(M)]
                cnf = cnf + exactly_one(v)

    # handle dots
    for constrain in constraints:
        # handle white dot
        if(constrain[4] == 'white'):
            combinations = []
            for i in range(0, N - 1):
                x1 = transformCell(itemgetter(*[0, 1])(constrain) + (i,))
                x2 = transformCell(itemgetter(*[2, 3])(constrain) + (i + 1,))
                x3 = transformCell(itemgetter(*[0, 1])(constrain) + (i + 1,))
                x4 = transformCell(itemgetter(*[2, 3])(constrain) + (i,))
                combinations.extend([[x1, x2], [x3, x4]])
            cnf.extend(itertools.product(*combinations))

        # handle a black dot
        if(constrain[4] == 'black'):
            combinations = []
            for i in range(1, N):
                for j in range(1, N):
                    if(j / 2 == i):
                        x1 = transformCell(itemgetter(
                            *[0, 1])(constrain) + (i - 1,))
                        x2 = transformCell(itemgetter(
                            *[2, 3])(constrain) + (j - 1,))
                        x3 = transformCell(itemgetter(
                            *[0, 1])(constrain) + (j - 1,))
                        x4 = transformCell(itemgetter(
                            *[2, 3])(constrain) + (i - 1,))
                        combinations.extend([[x1, x2], [x3, x4]])
            cnf.extend(itertools.product(*combinations))

    return cnf


'''
mean = 0

for dots in range(35, 62):
    total = 0
    counter = 0
    for sudoku in sudokus:
        if(len(sudokus[sudoku]["data"]) == dots):

            counter = counter + 1

            # start timer
            start_time = time.process_time()

            # constraints
            constraints = sudokus[sudoku]["data"]

            # make cnf
            cnf = makeCNF(constraints)

            # solve
            solution = pycosat.solve(cnf)

            # stop time and append it to the list
            runtime = time.process_time() - start_time

            total = total + runtime

    if(counter != 0):
        mean = total / counter
    print('dots: ', str(dots), 'mean: ', str(mean), 'length: ', str(counter))
'''

cnf = makeCNF(sudokus['059']["data"])

# print solutions
for solution in pycosat.itersolve(cnf):
    X = [inverse_transform(v) for v in solution if v > 0]
    sol = []
    for i, cell in enumerate(sorted(X, key=lambda h: h[0] * N * N + h[1] * N)):
        print(cell[2] + 1, " ", end='')
        sol.append(cell[2] + 1)
        if (i + 1) % N == 0:
            print(" ")
    print(" ")
    if sol == sudokus['059']["solution"]:
        print("Found the correct solution:")
        print(sol)
