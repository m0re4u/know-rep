# Author: Nicholas Pilkington, 2015
# License: MIT

import pycosat

N = 9
M = 3


def exactly_one(variables):
    cnf = [variables]
    n = len(variables)

    for i in xrange(n):
        for j in xrange(i + 1, n):
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


if __name__ == '__main__':
    cnf = []

    # Cell, row and column constraints
    for i in xrange(N):
        for s in xrange(N):
            cnf = cnf + exactly_one([transform(i, j, s) for j in xrange(N)])
            cnf = cnf + exactly_one([transform(j, i, s) for j in xrange(N)])

        for j in xrange(N):
            cnf = cnf + exactly_one([transform(i, j, k) for k in xrange(N)])

    # Sub-matrix constraints
    for k in xrange(N):
        for x in xrange(M):
            for y in xrange(M):
                v = [transform(y * M + i, x * M + j, k)
                     for i in xrange(M) for j in xrange(M)]
                cnf = cnf + exactly_one(v)

    # A 16-constraint Sudoku
    constraints = [
        (0, 3, 7),
        (1, 0, 1),
        (2, 3, 4),
        (2, 4, 3),
        (2, 6, 2),
        (3, 8, 6),
        (4, 3, 5),
        (4, 5, 9),
        (5, 6, 4),
        (5, 7, 1),
        (5, 8, 8),
        (6, 4, 8),
        (6, 5, 1),
        (7, 2, 2),
        (7, 7, 5),
        (8, 1, 4),
        (8, 6, 3),
    ]

    cnf = cnf + [[transform(z[0], z[1], z[2]) - 1] for z in constraints]

    for solution in pycosat.itersolve(cnf):
        X = [inverse_transform(v) for v in solution if v > 0]
        for i, cell in enumerate(sorted(X, key=lambda h: h[0] * N * N + h[1] * N)):
            print cell[2] + 1, " ",
            if (i + 1) % N == 0:
                print ""
