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



def parse_e(e): # function which takes a string of a fraction and returns a Fraction
    e = e.split("/")
    if len(e) == 1:
        return Fraction(int(e[0]), 1)
    else:
        return Fraction(int(e[0]), int(e[1]))

def parse_lp(filename):
    """ Create a Lp() object from a lp given in filename """

    print("PARSING...")
    with open(filename, "r") as f:
        n = int(f.readline()[:-1])
        m = int(f.readline()[:-1])

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

class Tableau():
    """ Structure which represents a tableau """
    
    def __init__(self, lp):
        """ Convert a linear programm to a tableau and add slack variables and variables for phase 1 """
        
        self.n = lp.m + 1 # n is the number of lines in the tableau
        self.m = lp.n + lp.m + 1 # m is the number of columns in the tableau
        self.basis = []
        self.phase_one = True
        self.vars_added = 0
        self.c = lp.c # we save the objective function for phase 2

        for i in range(0, lp.m):
            if lp.b[i] < 0: 
                self.basis.append(lp.n + lp.m + self.vars_added) # add variable for phase 1
                self.vars_added = self.vars_added + 1
            else:
                self.basis.append(lp.n + i) # add variable slack variable to the basis for phase 1

        self.m = self.m + self.vars_added
                
        self.tab = np.zeros((self.n, self.m), dtype=Fraction) # Creating the tableau

        for j in range(len(self.basis)): # add the objective function for phase 1
            if self.basis[j] >= lp.n + lp.m:
                self.tab[0, self.basis[j]] = -1

        temp = 0
        for i in range(1, self.n): # filling the tableau with each constraints
            for j in range(0, lp.n):
                self.tab[i, j] = lp.a[i-1, j]
            self.tab[i, lp.n + i - 1] = 1
            self.tab[i, -1] = lp.b[i-1]
            
            if lp.b[i-1] < 0: # taking the opposite line
                self.tab[i] = -self.tab[i]
                self.tab[i, lp.n + lp.m + temp] = 1 # add variable for phase 1
                temp = temp + 1

        for j in range(lp.n + lp.m, self.m - 1): # writing the obj vector in function of non basic vars
            if self.tab[0, j] != -1:
                continue
            for i in range(1, self.n):
                if self.tab[i, j] == 1:
                    self.tab[0] = self.tab[0] + self.tab[i]
                    break

    def do_pivot(self, entering_var, leaving_var):
        self.basis.remove(leaving_var)
        self.basis.append(entering_var)

        line = 0
        for i in range(1, self.m):
            if self.tab[i, leaving_var] == 1:
                line = i
                break;

        self.tab[line] = self.tab[line]/self.tab[line, entering_var]
        
        for i in range(0, self.n):
            if i == line:
                continue
            self.tab[i] = self.tab[i] - self.tab[i, entering_var] * self.tab[line]
            

    def print_tab(self):
        print("CURRENT TABLEAU")
        print(tabulate(self.tab))
        print("BASIS")
        print(self.basis)
        print("\n\n", end="")

    def get_basic(self):
        return self.basis

    def get_nonbasic(self):
        return [x for x in range(self.m - 1) if x not in self.basis]

    def basic_var_of_line(self, line): # returns the basic variable of the line
        for var in self.basis:
            if self.tab[line, var] == 1:
                return var
    
    def choose_entering_naive(self): # choose the entering var in a naive way
        var = None
        for j in range(0, self.m - 1):
            if self.tab[0, j] > 0:
                var = j
                break
            
        return var

    def choose_leaving_var(self, entering_var): # choose what is the leaving variable
        bound = None
        leaving_var = None
        for i in range(1, self.n):
            if self.tab[i, entering_var] > 0:
                if bound == None:
                    bound = self.tab[i, -1]/self.tab[i, entering_var]
                    leaving_var = self.basic_var_of_line(i)
                else:
                    temp = self.tab[i, -1]/self.tab[i, entering_var]
                    if temp < bound:
                        leaving_var = self.basic_var_of_line(i)
                        bound = temp

        return leaving_var
    

lin = parse_lp("phase1.in")
lin.print_lp()
t = Tableau(lin)
t.print_tab()

e_v = t.choose_entering_naive()
while e_v != None:
    l_v = t.choose_leaving_var(e_v)
    print("ENTERING VAR {}".format(e_v))
    print("LEAVING VAR {}".format(l_v))    
    t.do_pivot(e_v, l_v)
    t.print_tab()
    e_v = t.choose_entering_naive()

"""
print(" ----------------------------------")
lin = parse_lp("linear_problem2.in")
lin.print_lp()
t = Tableau(lin)
t.print_tab()
print(" ----------------------------------")
lin = parse_lp("linear_problem3.in")
lin.print_lp()
t = Tableau(lin)
t.print_tab()
"""
