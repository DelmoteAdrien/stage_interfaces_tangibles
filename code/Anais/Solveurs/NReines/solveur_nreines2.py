import time, collections
from ortools.sat.python import cp_model

#ces deux listes me permettent de nommer les variables
alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

num_reines = int(input("Nombre de reines : ")) #l'utilisateur doit saisir le nombre de reines
print()

model = cp_model.CpModel() #création du problème

tab = []
for k in range(num_reines):
    name = ""
    n = k//26
    tab2 = [n]
    while(n>25):
        n = n//26
        tab2.append(n)
    name = name + alpha[tab2[len(tab2)-1]]
    for l in range(len(tab2)-1):
        name = name + alpha[tab2[len(tab2)-1-l]//(26*(len(tab2)-1-l))]
    name = Alpha[k%26] + name
    tab.append(model.new_int_var(1, num_reines, name))
    """
    if (k<=25):
        tab.append(model.new_int_var(1, num_reines, alpha[k]))
    else:
        tab.append(model.new_int_var(1, num_reines, Alpha[k-26]))
    """

for i in range(num_reines-1):
    for j in range(i+1,num_reines):
        model.add(tab[i]!=tab[j])
        model.add(tab[i]+j!=tab[j]+i)
        model.add(tab[i]-j!=tab[j]-i)

solver = cp_model.CpSolver() #création d'un solveur du problème
debut = time.perf_counter() #debut de la recherche d'une solution
status = solver.solve(model) #recherche d'une solution
fin = time.perf_counter() #fin de la recherche d'une solution

def affichage_echiquier():
    ch = "Affichage des coordonnees (x,y) des reines telles que 1 <= x,y <= " + str(num_reines) + " :\n"
    for i in range(num_reines):
        """
        ch += "----"*num_reines + "-" + "\n"
        for j in range(num_reines):
            if (solver.value(tab[i])==j+1):
                ch += "| X "
            else:
                ch += "|   "
        ch += "|\n"
        """
        ch += "Reine n°" + str(i+1) + " : (" + str(i+1) + ","  + str(solver.value(tab[i])) + ")\n"
    #ch += "----"*num_reines + "-"
    return ch

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    """
    for i in range(num_reines):
        print(solver.value(tab[i]))
    """
    print(affichage_echiquier())
else:
    print("Pas de solution.")

print("Duree de la recherche d'une solution = ",(fin-debut),"s")