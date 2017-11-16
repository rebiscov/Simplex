import numpy as np
import sys
from tabulate import *
from fractions import Fraction
from random import randint

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
        self.c = lp.c.copy() # we save the objective function for phase 2
        self.basic_var_line = []

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

        self.basic_of_line = self.m * [-1]
        for var in self.basis:
            for i in range(1, self.m):
                if self.tab[i, var] == 1:
                    self.basic_of_line[i] = var
                    break

    def do_pivot(self, entering_var, leaving_var):
        self.basis.remove(leaving_var)
        self.basis.append(entering_var)

        line = 0
        for i in range(1, self.m):
            if self.tab[i, leaving_var] == 1:
                line = i
                break;

        self.basic_of_line[line] = entering_var

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

    def write_obj_vector(self): # once phase1 is completed, preparing for phase2
        self.tab = np.delete(self.tab, np.s_[self.m -1 - self.vars_added:-1], 1)
        self.m = self.m - self.vars_added        
        
        for j in range(len(self.c)):
            self.tab[0, j] = self.c[j]

        for j in range(len(self.c), self.m):
            self.tab[0, j] = 0

        for i in range(1, self.n):
            var_of_basis = self.basic_var_of_line(i)
            self.tab[0] = self.tab[0] - self.tab[0, var_of_basis] * self.tab[i]

        self.basic_of_line = self.basic_of_line[:self.m]
            

    def get_basic(self):
        return self.basis

    def get_nonbasic(self):
        return [x for x in range(self.m - 1) if x not in self.basis]

    def basic_var_of_line(self, line): # returns the basic variable of the line
        """
        for var in self.basis:
            if self.tab[line, var] == 1:
                return var
        """
        return self.basic_of_line[line]
    
    def choose_entering_naive(self): # choose the entering var in a naive way, it naturally follows Bland's rules
        var = None
        for j in range(0, self.m - 1):
            if self.tab[0, j] > 0:
                var = j
                break
            
        return var

    def choose_entering_max_coeff(self): # choose the to add in the basis the variable with the biggest coefficient in the objective vector
        var = None
        for j in range(0, self.m - 1):
            if self.tab[0, j] > 0 and var == None:
                var = j
            elif var != None and self.tab[0, var] < self.tab[0, j]:
                var = j

        return var

    def choose_entering_random(self):
        L = []
        for j in range(0, self.m - 1):
            if self.tab[0, j] > 0:
                L.append(j)

        if L == []:
            return None
        else:
            return L[randint(0, len(L) - 1)]

    def choose_leaving_var(self, entering_var): # choose what is the leaving variable, returns None if it is unbounded, applies Bland's rules
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
                    elif temp == bound: # if there is a tie, applies Bland's rules
                        if leaving_var < self.basic_var_of_line(i):
                            leaving_var = self.basic_var_of_line(i)
                            bound = temp

        return leaving_var

    def phase(self, entering):
        self.choose_entering = entering

        e_v = self.choose_entering()
        while e_v != None:
            l_v = self.choose_leaving_var(e_v)

            if l_v == None: # meaning the linear problem is unbounded
                return None
            
            print("ENTERING VAR {}".format(e_v))
            print("LEAVING VAR {}".format(l_v))    
            self.do_pivot(e_v, l_v)
            self.print_tab()
            e_v = self.choose_entering()
            
        return self.tab[0, -1]

    def solve_simplex(self, pivot_rule = None):
        if pivot_rule == None:
            choose_entering = self.choose_entering_naive
        elif pivot_rule == "m":
            choose_entering = self.choose_entering_max_coeff
        elif pivot_rule == "r":
            choose_entering = self.choose_entering_random

        print("BEGINNING OF PHASE 1")
        self.print_tab()
        
        self.phase(choose_entering)

        if self.tab[0, -1] != 0:
            print("The linear problem is INFEASIBLE")
            return
        
        print("END OF PHASE 1\n")
        
        print("BEGINNING OF PHASE 2")
        t.write_obj_vector()
        self.print_tab()

        if self.phase(choose_entering) == None:
            print("The linear problem is unbounded")
        else:
            print("END OF PHASE 2")
            print("Here is the final tableau")
            self.print_tab()
            print("The optimal value is {}".format(-self.tab[0, -1]))
            

if len(sys.argv) > 1:
    lin = parse_lp(sys.argv[1])
    lin.print_lp()
    t = Tableau(lin)
    t.solve_simplex("r")
else:
    print("No file has been given.")

