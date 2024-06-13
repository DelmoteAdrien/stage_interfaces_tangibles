import time, collections
from ortools.sat.python import cp_model

alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

n = int(input("Nombre de billes : ")) #saisie du nombre de billes
m = int(input("Nombre de boites : ")) #saisie du nombre de boites

model = cp_model.CpModel()

tab = []

#initialisation des variables
for k in range(n):
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
    tab.append(model.new_int_var(1, m, name))

#initialisation des contraintes
for y in range(n):
    for x in range(y+1,n):
        if (x==2*y): #Si x=2y, alors les billes n°x et n°y ne doivent pas être dans la même boîte
            model.add(tab[x]!=tab[y])
        else:
            for z in range(x+1,n):
                if (x+y==z): #Si x+y=z, alors les billes n°x et n°y ne doivent pas être dans la même boîte que la bille n°z
                    model.add(tab[x]!=tab[z])
                    model.add(tab[y]!=tab[z])

# Create a solver and solve.
solver = cp_model.CpSolver()
# Solve.
debut = time.perf_counter() #debut de la recherche de solutions
status = solver.solve(model)
fin = time.perf_counter() #fin de la recherche de solutions

print()
print("Duree de la recherche d'une solution = ",(fin-debut),"s") #affichage de la durée de recherche d'une solution

#Affichage d'une solution
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for i in range(n):
        print(f"Boite de la bille n°{i+1} = {solver.value(tab[i])}")
else:
    print("Pas de solution trouvee.")
