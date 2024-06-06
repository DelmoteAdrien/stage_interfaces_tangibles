import time, collections
from ortools.sat.python import cp_model

"""
problème de Shurr :
Sujet : On a n billes numérotées de 1 à n et m boites.
But: chaque bille doit être dans les boîtes
contraint: Pour tout x,y,z numéros de billes dans une même boîte :
- x=/=2*y
- x+y!=z
interface T+C: possible
interface inForm: possible
"""

alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

n = int(input("Nombre de billes : "))
m = int(input("Nombre de boites : "))

model = cp_model.CpModel()

tab = []

for k in range(n):
    if (k<=25):
        tab.append(model.new_int_var(0, m-1, alpha[k]))
    else:
        tab.append(model.new_int_var(0, m-1, Alpha[k-26]))

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
print("Duree de la recherche de solutions = ",(fin-debut),"s")

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for i in range(n):
        print(f"{tab[i]} = {solver.value(tab[i])}")
else:
    print("Pas de solution trouvee.")