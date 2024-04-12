# First we need to print clauses
import sys

from sat.solver.pysat.src.pysat import Solver, readFile


def printClause(clause):
    print(" ".join([str(v) for v in clause]) + " 0")


def equals1a(arrayOfVars):
    printClause(arrayOfVars) 
    for i,x in enumerate(arrayOfVars):
        for y in arrayOfVars[i+1:]:
            printClause([-x, -y])


def case_valid(coord):
    equals1a([coord + i for i in range(1, 10)])


def row_has_number(row, number):
    equals1a([row + col + number for col in range(10, 100, 10)])


def col_has_number(col, number):
    equals1a([row + col + number for row in range(100, 1000, 100)])


def square_has_number(i, j, number):
    row_offset = i * 300
    col_offset = j * 30
    equals1a([row + col + number for row in range(100 + row_offset, 400 + row_offset, 100) for col in range(10 + col_offset, 40 + col_offset, 10)])


def sudoku_constraints():
    # cases
    for row in range(100, 1000, 100):
        for col in range(10, 100, 10):
            case_valid(row + col)

    # row constraints
    for row in range(100, 1000, 100):
        for number in range(1, 10, 1):
            row_has_number(row, number)

    # col constraints
    for col in range(10, 100, 10):
        for number in range(1, 10, 1):
            col_has_number(col, number)

    # squares
    for i in range(3):
        for j in range(3):
            for number in range(1, 10):

                square_has_number(i, j, number)


def diabolic():
    info = [184,
            234, 269, 275, 291,
            345, 376, 397,
            426, 435, 471,
            517, 521, 543, 566, 582, 594,
            639, 673, 686,
            718, 737, 763,
            815, 831, 847, 878,
            923]

    for i in info:
        print(i, end=" 0\n")



filename = "solver/pysat/src/sudokuDimacs.cnf"
with open(filename, "w+") as file:
    sys.stdout = file
    sudoku_constraints()
    diabolic()
    sys.stdout = sys.__stdout__


solver = Solver()
readFile(solver, filename)
solver.buildDataStructure()
result = solver.solve()
res = list(filter(lambda x: x >= 0, solver.finalModel))


res.sort()
res = [list(map(lambda x: str(x % 10), res))[i * 9:(i + 1) * 9:] for i in range(9)]
print(*res, sep="\n")
