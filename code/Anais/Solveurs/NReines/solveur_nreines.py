import time, collections
from ortools.sat.python import cp_model

num_reines = int(input("Nombre de reines : "))

alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables: list[cp_model.IntVar]):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self) -> None:
        self.__solution_count += 1
        for v in self.__variables:
            print(f"{v}={self.value(v)}", end=" ")
        print()

    @property
    def solution_count(self) -> int:
        return self.__solution_count

def search_for_all_solutions_sample_sat():
    """Showcases calling the solver to search for all solutions."""
    # Creates the model.
    model = cp_model.CpModel()

    tab = [] #ensemble des variables représentant une reine à chaque ligne de l'échiquier

    for k in range(num_reines):
        if (k<=25):
            tab.append(model.new_int_var(0, num_reines-1, alpha[k]))
        else:
            tab.append(model.new_int_var(0, num_reines-1, Alpha[k-26]))

    for i in range(len(tab)):
        for j in range(i+1,len(tab)):
            model.add(tab[i] != tab[j]) #2 reines ne doivent pas être à la même colonne
            #Note : chaque variable représente une ligne dans laquelle se trouve une reine
            #donc pas besoin de mettre une contrainte alldiff pour les lignes
            if (abs(i-j)==1): #les colonnes de 2 reines ne doivent pas être côte à côte
                model.add(tab[i] != (tab[j]-1))
                model.add(tab[i] != (tab[j]+1))

    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter(tab)
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    # Solve.
    debut = time.perf_counter() #debut de la recherche de solutions
    status = solver.solve(model, solution_printer)
    fin = time.perf_counter() #fin de la recherche de solutions

    print()
    print("Duree de la recherche de solutions = ",(fin-debut),"s")
    print(f"Statut = {solver.status_name(status)}")
    print(f"Nombre de solutions trouvees : {solution_printer.solution_count}")


search_for_all_solutions_sample_sat()

"""
3 juin 2024 :
Durée de la dernière recherche de solutions pour n = 4 : 0.006311891000223113 s
Durée de la dernière recherche de solutions pout n = 10 : 77.19015956600015 s
"""

#J'ai pu mettre 27 reines (donc une variable A) sans trop de pb
#Juste une recherche de solution trop longue que je vais pas finir
#Il semble que l'ordi ne se plante jamais, là-dessus