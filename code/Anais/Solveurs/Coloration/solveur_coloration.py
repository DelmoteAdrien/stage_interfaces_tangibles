import time, collections
from ortools.sat.python import cp_model

#ces deux listes me permettent de nommer les variables
alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#lecture d'un fichier
#filin = open("graphe.txt","r")

#name1 = "GraphColoring/GraphColoring-m1-mono/GraphColoring-1-fullins-3.xml"
#name2 = "GraphColoring.tgz/./GraphColoring/GraphColoring-m1-mono/GraphColoring-1-fullins-3.xml.lzma/GraphColoring-1-fullins-3.xml"
#name3 = "\""

name = "GraphColoring/GraphColoring-m1-mono/GraphColoring-1-fullins-3.xml"
filin = open(name,"r")
lignes = filin.readlines()

"""
for i in range(len(lignes[2])):
    print(lignes[2][i])
for j in range(len(name3)):
    print(name3[j])
print(len(name3))
"""

c = 0

while(lignes[2][c]!="\""):
    c += 1
id = ""
c += 1
while(lignes[2][c]!="\""):
    id = id + lignes[2][c]
    c += 1
#print(id)

n = 1
while(lignes[2][c]!=str(n)):
    if (lignes[2][c]!=str(n)):
        n += 1
    if (n==10):
        n = 1
        c += 1
number = ""
while(lignes[2][c]!="]"):
    number = number + lignes[2][c]
    c += 1
s = int(number) #Nombre de sommets
c = c+4

"""
while(lignes[2][c]!=str(n)):
    print("c = ",c)
    print("n = ",n)
    if (lignes[2][c]!=str(n)):
        n += 1
    if (n==10):
        n = 1
        c += 1
"""

minimum = ""
while(lignes[2][c]!="."):
    minimum = minimum + lignes[2][c]
    c += 1
min = int(minimum)
max = s - 1 + min
#A = int(lignes[1][0]) #Nombre d'arcs

arcs = [[0 for j in range(s)] for i in range(s)] #liste de nombres binaires representants les arcs

"""
#attribuer les arcs selon ce qui est lu dans le fichier
for ind in range(A):
    D = lignes[ind+2][0] #premier sommet de l'arc
    i = Alpha.find(D)
    F = lignes[ind+2][1] #deuxieme sommet de l'arc
    j = Alpha.find(F)
    arcs[i][j]=1 #arc DF existe
    arcs[j][i]=1 #arc FD existe (note : DF = FD)
"""

L = 9
c = 0
nb = 0
while(L<len(lignes)):
    #print("L = ",L)
    #print("len(lignes[L]) =", len(lignes[L]))
    D = 0
    F = 0
    debut = ""
    fin = ""
    if (lignes[L][c-1]=="["):
        #while(nb<2):
        while(lignes[L][c]!="]"):
            #print("c = ",c)
            n = 0
            while((n<10)&(lignes[L][c]!=str(n))):
                n = n+1
            if (lignes[L][c]==str(n)):
                debut = debut + lignes[L][c]
            c += 1
        if (len(debut)>0):
            c += 3 + len(id)
            while(lignes[L][c]!="]"):
                #print("c = ",c)
                n=0
                while((n<10)&(lignes[L][c]!=str(n))):
                    n = n+1
                if (lignes[L][c]==str(n)):
                    fin = fin + lignes[L][c]
                c += 1
        if ((len(debut)>0)&(len(fin)>0)):
            D = int(debut)
            F = int(fin)
            arcs[D][F]=1 #arc DF existe
            arcs[F][D]=1 #arc FD existe (note : DF = FD)
    c = c+1
    if (c==len(lignes[L])):
        c = 0
        L = L+1

model = cp_model.CpModel() #initialisation du problème

#initialisation des variables (sommets)
tab = []
for k in range(s):
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
    tab.append(model.new_int_var(min, max, name))
    #tab.append(model.new_int_var(0, s-1, Alpha[k]))

#initialisation des contraintes
for i in range(s):
    for j in range(s):
        if ((arcs[i][j]==1)&(i!=j)): #si 2 sommets différents sont reliés
            model.add(tab[i]!=tab[j]) #leur couleur doit être différente

solver = cp_model.CpSolver() #création d'un solveur du problème
debut = time.perf_counter() #debut de la recherche d'une solution
status = solver.solve(model) #recherche d'une solution
fin = time.perf_counter() #fin de la recherche d'une solution

print("Duree de la recherche d'une solution = ",(fin-debut),"s\n")

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE: #si le problème est résoluble
    for i in range(s):
        print(f"{tab[i]} = {solver.value(tab[i])}")
else:
    print("Pas de solution trouvee.") #sinon