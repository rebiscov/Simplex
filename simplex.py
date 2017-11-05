import numpy as np
from tabulate import *
from fractions import Fraction

class Lp:
    """ class that will store the linear problem """
    def __init__(self, n, m, constraints_matrix, constraints_vector, objective_vector):
        self.n = n
        self.m = m
        self.a = constraints_matrix
        self.b = constraints_vector
        self.c = objective_vector

    def print_lp(self):
        lp = [["" for j in range(0, self.n+3)] for i in range(0, self.m+2)]

        lp[0][0] = "Maximize"
        lp[1][0] = "Such that"

        for i in range(1, self.m+1):
            for j in range(1, self.n+1):
                if j == 1:
                    x = ""
                else:
                    x = "+"
                    
                lp[i][j] = x + str(self.a[i-1,j-1]) + "x_" + str(j)

        for j in range(1, self.n+1):
            if j == 1:
                x = ""
            else:
                x = "+"
            
            lp[0][j] = x + str(self.c[j-1]) + "x_" + str(j)

        for i in range(1, self.m+1):
            lp[i][-1] = "<= " + str(self.b[i-1])
                
        print(tabulate(lp))

class Tableau():
    """ Structure which represents a tableau """
    
    def __init__(self, lp):
        """ Convert a linear programm to a tableau and add slack variables """
        
        self.n = lp.m + 1
        self.m = lp.n + lp.m + 1
        
        self.tab = np.empty((self.n, self.m), dtype=Fraction)

        print(lp.a)
        print(lp.n, lp.m)

        for i in range(0, self.n):
            for j in range(0, self.m):
                self.tab[i, j] = Fraction(0,1)

        for i in range(1, lp.m+1):
            for j in range(0, lp.n):
                print((i, j))
                self.tab[i,j] = lp.a[i-1, j]


def parse_e(e):
    e = e.split("/")
    if len(e) == 1:
        return Fraction(int(e[0]), 1)
    else:
        return Fraction(int(e[0]), int(e[1]))

def parse_lp(filename):
    print("PARSING...")
    with open(filename, "r") as f:
        n = int(f.readline()[0])
        m = int(f.readline()[0])

        temp = f.readline().split()
        c = []
        for e in temp:
            c.append(parse_e(e))

        temp = f.readline().split()
        b = []
        for e in temp:
            b.append(parse_e(e))

        a = []
        for temp in f:
            temp = temp.split()
            a.append([])
            for e in temp:
                a[-1].append(parse_e(e))

        print("PARSING FINISHED.")

        return Lp(n, m, np.array(a), np.array(b), np.array(c))
    

lin = parse_lp("linear_problem.in")
lin.print_lp()
t = Tableau(lin)
print(tabulate(t.tab))
