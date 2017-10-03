# author: Petra Ormel & Michiel van der Meer, 2017

from operator import itemgetter
import itertools
import json
import sys
import pycosat
import re

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

# 9 * 9 * 9 variables for standard sudoku
nVar = 729


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


def getNextVar():
    global nVar
    x = nVar
    nVar += 1
    return x


def inverse_transform(v):
    if v <= N * N * N:
        # Only print the values that represent a digit in a cell
        v, k = divmod(v - 1, N)
        v, j = divmod(v, N)
        v, i = divmod(v, N)
    else:
        # this is a helper variable, contains no extra information
        return None
    return i, j, k


def transformCell(cell):
    return cell[0] * N * N + cell[1] * N + cell[2] + 1


def transformBorder(var1, var2):
    """
    Get variables used in the improved encoding
    """
    if var1[0] - var2[0] != 0:
        # horizontal border
        print("hor")
        print(var1)
        return N * N * N + N * N * var1[0] + N * var1[1] + var1[2]
    elif var1[1] - var2[1] != 0:
        # vertical border
        print("ver")
        return N * N * N + N * N * var1[0] + N * var1[1] + var1[2] + 1
    else:
        return
    return N * N * N + N * var1 + var2


cnf = []

# Cell, row and column constraints
for i in range(N):
    for s in range(N):
        cnf = cnf + exactly_one([transform(i, j, s) for j in range(N)])
        cnf = cnf + exactly_one([transform(j, i, s) for j in range(N)])

    for j in range(N):
        cnf = cnf + exactly_one([transform(i, j, k) for k in range(N)])

# Sub-matrix constraints - blocks!
for k in range(N):
    for x in range(M):
        for y in range(M):
            v = [transform(y * M + i, x * M + j, k)
                 for i in range(M) for j in range(M)]
            cnf = cnf + exactly_one(v)

# Constraints given by kropki
constraints = sudokus["057"]["data"]
# Count constraints
white_counter = 0
black_counter = 0
# Count clauses added per contraint type
white_added = 0
black_added = 0

for constrain in constraints:
    # handle a white dot
    if(constrain[4] == 'white'):
        white_counter += 1
        combinations = []
        for i in range(N):
            x1 = transformCell((constrain[0], constrain[1], i))
            x2 = transformCell((constrain[2], constrain[3], i + 1))
            x3 = transformCell((constrain[0], constrain[1], i + 1))
            x4 = transformCell((constrain[2], constrain[3], i))
            combinations.extend([[x1, x2], [x3, x4]])
        newlist = []
        helper_vars = []
        for comb in combinations:
            dvar = getNextVar()
            newlist.extend([[-dvar, comb[0]], [-dvar, comb[1]]])
            helper_vars.append(dvar)
        cnf.append(helper_vars)
        cnf.extend(newlist)
        white_added += len(newlist) + 1

    # handle a black dot
    if(constrain[4] == 'black'):
        black_counter += 1
        combinations = []
        for i in range(1, N):
            for j in range(1, N):
                if(j / 2 == i):
                    x1 = transformCell((constrain[0], constrain[1], i - 1))
                    x2 = transformCell((constrain[2], constrain[3], j - 1))
                    x3 = transformCell((constrain[0], constrain[1], j - 1))
                    x4 = transformCell((constrain[2], constrain[3], i - 1))
                    combinations.extend([[x1, x2], [x3, x4]])
        helper_vars = []
        newlist = []
        for comb in combinations:
            dvar = getNextVar()
            newlist.extend([[-dvar, comb[0]], [-dvar, comb[1]]])
            helper_vars.append(dvar)
        black_added += len(newlist) + 1
        cnf.append(helper_vars)
        cnf.extend(newlist)


print("Generated {} clauses for {} white circles and {} black circles".format(len(cnf), white_counter, black_counter))
print("White clauses: {} | black clauses: {}".format(white_added, black_added))
N_solutions = 0
for solution in pycosat.itersolve(cnf, verbose=0):
    X = [inverse_transform(v) for v in solution if v > 0 and inverse_transform(v) is not None]
    N_solutions += 1
    sol = []
    for i, cell in enumerate(sorted(X, key=lambda h: h[0] * N * N + h[1] * N)):
        print(cell[2] + 1, " ", end='')
        sol.append(cell[2] + 1)
        if (i + 1) % N == 0:
            print(" ")
    print(" ")
    if sol == sudokus["057"]["solution"]:
        print("Found the correct solution:")
        print(sol)
print("Found {} solutions!".format(N_solutions))
