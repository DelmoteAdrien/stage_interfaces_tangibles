import time, collections
from ortools.sat.python import cp_model

alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

cases = [[Alpha[i] + alpha[j] for j in range(9)] for i in range(9)] #nom des cases
pleines = [] #liste de cases pleines

#lecture du fichier
filin = open("sudoku.txt","r")
lignes = filin.readlines()
for k in range(len(lignes)): #lecture des cases pleines
    pleines2 = [int(lignes[k][0]),int(lignes[k][2]),int(lignes[k][4])]
    pleines.append(pleines2)
            
model = cp_model.CpModel()

tab = []

#initialisation des variables (cases)
for i in range(9):
    tab.append([])
    for j in range(9):
        tab[i].append(model.new_int_var(1, 9, cases[i][j]))

#initialisation des contraintes
for i in range(9): #contraintes dans une ligne
    for j in range(9): #contraintes dans une colonne
        for n in range(1,10): #remplir cases pleines
            if ([i,j,n] in pleines):
                model.add(tab[i][j]==n)
        for k in range(9):
            if (j!=k): #les cases d'une même ligne ne doivent pas être identiques
                model.add(tab[i][j]!=tab[i][k])
            if (i!=k): #les cases d'une même colonne ne doivent pas être identiques
                model.add(tab[i][j]!=tab[k][j])

#contraintes dans une même sous-partie 3*3 d'un sudoku
for L in range(3):
    for l in range(3):
        for m in range(3):
            for C in range(3):
                for c in range(3):
                    for n in range(3):
                        if ((l!=m)|(c!=n)):
                            model.add(tab[3*L+l][3*C+c]!=tab[3*L+m][3*C+n]) #les cases d'une même sous-partie 3*3 ne doivent pas être identiques

# Create a solver and solve.
solver = cp_model.CpSolver()
# Solve.
debut = time.perf_counter() #debut de la recherche de solutions
status = solver.solve(model)
fin = time.perf_counter() #fin de la recherche de solutions

print("Duree de la recherche d'une solution = ",(fin-debut),"s\n")

def affichage_sudoku(): #affichage de la grille obtenue du sudoku
    ch = ""
    for i in range(9):
        ch += "-----"*7 + "--" + "\n"
        for j in range(9):
            ch += "| " + str(solver.value(tab[i][j])) + " "
        ch += "|\n"
    ch += "-----"*7 + "--"
    return ch

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE: #s'il existe une solution, afficher la grille
    print(affichage_sudoku())
