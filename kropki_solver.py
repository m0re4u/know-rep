# author: Petra Ormel, 2017

from operator import itemgetter
import itertools
import json
import sys
import pycosat

with open('parsed.json') as data_file:    
    data = json.load(data_file)

print('Kripki puzzel:', data[0][0])

#constants
N = 9
M = 3

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

constraints = data[0][1]


for constrain in constraints:
	# handle a white dot
	if(constrain[4] == 'white'):
		combinations = []
		for i in range(0, N-1):
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
				if(j/2 == i):
					x1 = transformCell(itemgetter(*[0, 1])(constrain) + (i-1,))
					x2 = transformCell(itemgetter(*[2, 3])(constrain) + (j-1,))
					x3 = transformCell(itemgetter(*[0, 1])(constrain) + (j-1,))
					x4 = transformCell(itemgetter(*[2, 3])(constrain) + (i-1,))
					combinations.extend([[x1, x2], [x3, x4]])
		cnf.extend(itertools.product(*combinations))

		
print(len(cnf))

for solution in pycosat.itersolve(cnf):
    X = [inverse_transform(v) for v in solution if v > 0]
    for i, cell in enumerate(sorted(X, key=lambda h: h[0] * N * N + h[1] * N)):
        print (cell[2] + 1, " ", end='')
        if (i + 1) % N == 0:
            print (" ")

    print(" ")
