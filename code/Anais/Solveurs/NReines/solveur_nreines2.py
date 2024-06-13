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
    #une manière de nommer les variables permettant en théorie de mettre le nombre de variables qu'on veut
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

#initialisation des contraintes
for i in range(num_reines-1):
    for j in range(i+1,num_reines):
        model.add(tab[i]!=tab[j]) #deux reines ne peuvent pas être dans la même colonne
        model.add(tab[i]+j!=tab[j]+i) #deux reines ne peuvent pas être dans la même diagonale gauche
        model.add(tab[i]-j!=tab[j]-i) #deux reines ne peuvent pas être dans la même diagonale droite
#Note : deux reines ne peuvent pas être dans la même ligne, mais ici chaque reine représente une ligne différente, donc pas besoin d'implémenter cette contrainte

solver = cp_model.CpSolver() #création d'un solveur du problème
debut = time.perf_counter() #debut de la recherche d'une solution
status = solver.solve(model) #recherche d'une solution
fin = time.perf_counter() #fin de la recherche d'une solution

def affichage_echiquier(): #affichage des coordonnées des reines
    ch = "Affichage des coordonnees (x,y) des reines telles que 1 <= x,y <= " + str(num_reines) + " :\n"
    for i in range(num_reines):
        ch += "Reine n°" + str(i+1) + " : (" + str(i+1) + ","  + str(solver.value(tab[i])) + ")\n"
    return ch

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE: #s'il existe une solution
    print(affichage_echiquier())
else: #sinon
    print("Pas de solution.")

print("Duree de la recherche d'une solution = ",(fin-debut),"s") #affichage de la durée de recherche d'une solution