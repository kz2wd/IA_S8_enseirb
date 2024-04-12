import sys
from enum import IntEnum

from sat.solver.pysat.src.pysat import Solver, readFile


class Pawn(IntEnum):
    MONSTER = 1
    SMELL = 2
    HOLE = 3
    WIND = 4
    GOLD = 5


__GRIDSIZE__ = 4


def inBound(x):
   if x < 0 or x >= __GRIDSIZE__: return False
   return True

def around(coord):
   (x,y) = coord
   toret = []
   for (dx,dy) in [(-1,0), (0,1), (1,0), (0,-1)]:
      if inBound(dx+x) and inBound(dy+y):
         toret.append((dx+x, dy+y))
   return toret

def varToStr(symbol, coord):
   return f"{symbol}{coord[0]}{coord[1]}"

def printConstraint(symbol1, symbol2, coord):
   for (x,y) in around(coord):
      print("-" + varToStr(symbol1, coord)+" "+varToStr(symbol2,(x,y)), end=" 0\n")

def printConstraintNeg(symbol1, symbol2, coord):
   for (x,y) in around(coord):
      print(varToStr(symbol1, coord)+" "+varToStr(symbol2,(x,y)), end=" 0\n")

def printExclusionConstraint(symbol1, symbol2, coord):
   print("-" + varToStr(symbol1,coord) + " -" + varToStr(symbol2,coord), end=" 0\n")
   print("-" + varToStr(symbol2,coord) + " -" + varToStr(symbol1,coord), end=" 0\n")

def printAllConstraints(coord):
   printConstraint(Pawn.HOLE, Pawn.WIND, coord) # A Hole implies wind all around
   printConstraint(Pawn.MONSTER, Pawn.SMELL, coord) # A Monster implies odors all around
   printConstraintNeg(Pawn.SMELL, Pawn.MONSTER, coord) # No Odor means no monster all around
   printConstraintNeg(Pawn.WIND, Pawn.HOLE, coord) # No wind implies no hole all around
   printExclusionConstraint(Pawn.MONSTER,Pawn.HOLE,coord) # A cell cannot contain a Monster and a Hole
   printExclusionConstraint(Pawn.GOLD,Pawn.HOLE,coord) # A cell cannot contain a Gold and a Hole
   printExclusionConstraint(Pawn.GOLD,Pawn.MONSTER,coord) # A cell cannot contain a Gold and a Monster



observations = [f"-{Pawn.SMELL}00 0", f"-{Pawn.WIND}00 0"]
deductions = []

def build_file(hypothesis):
    with open(filename, "w+") as file:

        sys.stdout = file
        for x in range(__GRIDSIZE__):
          for y in range(__GRIDSIZE__):
            printAllConstraints((x, y))

        for obs in observations:
            print(obs)
        for ded in deductions:
            print(ded)

        print(hypothesis)

        sys.stdout = sys.__stdout__


filename = "monsterDimacs.cnf"


def test(hypothesis):
    build_file(hypothesis)
    solver = Solver()
    readFile(solver, filename)
    solver.buildDataStructure()
    result = solver.solve()
    if result == 0:
        deductions.append("-" + hypothesis)


