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
        lp = [["" for j in range(0, self.m+3)] for i in range(0, self.n+2)]

        lp[0][0] = "Maximize"
        lp[1][0] = "Such that"

        for i in range(1, self.n+1):
            for j in range(1, self.m+1):
                if j == 1:
                    x = ""
                else:
                    x = "+"
                    
                lp[i][j] = x + str(self.a[i-1,j-1]) + "x_" + str(j)

        for j in range(1, self.m+1):
            if j == 1:
                x = ""
            else:
                x = "+"
            
            lp[0][j] = x + str(self.c[j-1]) + "x_" + str(j)

        for i in range(1, self.n+1):
            lp[i][-1] = "<= " + str(self.b[i-1])
                
        print(tabulate(lp)) 

lin = Lp(2, 2, np.array([Fraction(1,2),2,3,4]).reshape(2,2), np.array([2,6]), np.array([4,9]))

lin.print_lp()
