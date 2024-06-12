import time, collections
from ortools.sat.python import cp_model

alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

cases = [[Alpha[i] + alpha[j] for j in range(9)] for i in range(9)]
pleines = []

ajout = int(input("Remplir une case pour le depart ? (non=0 et oui=1) : "))
while((ajout<0)|(ajout>1)):
    ajout = int(input("0 pour non ou 1 pour oui : "))
print()

if (ajout==1):
    ajout2 = True
    while(ajout2):
        pleines2 = []
        ligne = -1
        while ((ligne<0)|(ligne>8)):
            ligne = int(input("Numero de la ligne (entre 1 et 9) : "))-1
        pleines2.append(ligne)
        colonne = -1
        while ((colonne<0)|(colonne>8)):
            colonne = int(input("Numero de la colonne (entre 1 et 9) : "))-1
        pleines2.append(colonne)
        num = 0
        while ((num<1)|(num>9)):
            num = int(input("Numero de la case (entre 1 et 9) : "))
        pleines2.append(num)
        pleines.append(pleines2)
        print()
        ajout = int(input("Remplir une autre case pour le depart ? (non=0 et oui=1) : "))
        while((ajout<0)|(ajout>1)):
            ajout = int(input("0 pour non ou 1 pour oui : "))
        if (ajout==0):
            ajout2 = False

model = cp_model.CpModel()

tab = []

for i in range(9):
    tab.append([])
    for j in range(9):
        tab[i].append(model.new_int_var(1, 9, cases[i][j]))

for i in range(9):
    for j in range(9):
        for n in range(1,10):
            if ([i,j,n] in pleines):
                model.add(tab[i][j]==n)
        for k in range(9):
            if (j!=k): #les cases d'une même ligne ne doivent pas être identique
                model.add(tab[i][j]!=tab[i][k])
            if (i!=k): #les cases d'une même colonne ne doivent pas être identique
                model.add(tab[i][j]!=tab[k][j])

#contraintes dans une même sous-partie 3*3 d'un sudoku
for L in range(3):
    for l in range(3):
        for m in range(3):
            for C in range(3):
                for c in range(3):
                    for n in range(3):
                        if ((l!=m)|(c!=n)):
                            model.add(tab[3*L+l][3*C+c]!=tab[3*L+m][3*C+n])

# Create a solver and solve.
solver = cp_model.CpSolver()
# Solve.
debut = time.perf_counter() #debut de la recherche de solutions
status = solver.solve(model)
fin = time.perf_counter() #fin de la recherche de solutions

print()
print("Duree de la recherche d'une solution = ",(fin-debut),"s")

def affichage_sudoku():
    ch = ""
    for i in range(9):
        ch += "-----"*7 + "--" + "\n"
        for j in range(9):
            ch += "| " + str(solver.value(tab[i][j])) + " "
        ch += "|\n"
    ch += "-----"*7 + "--" + "\n"
    return ch

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(affichage_sudoku())