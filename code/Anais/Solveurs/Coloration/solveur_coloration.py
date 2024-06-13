import time, collections
from ortools.sat.python import cp_model

#ces deux listes me permettent de nommer les variables
alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

name = "GraphColoring/GraphColoring-m1-mono/GraphColoring-1-fullins-4.xml"
filin = open(name,"r")
lignes = filin.readlines()

#Dans la ligne 2

c = 0 #colonne

#Pour prendre l'identifiant (dans le fichier utilisé ici, c'est x)
while(lignes[2][c]!="\""): #Arrivée vers l'identifiant
    c += 1
id = ""
c += 1
while(lignes[2][c]!="\""): #Lecture de l'identifiant
    id = id + lignes[2][c]
    c += 1

#Pour prendre le nombre de sommets
n = 1
while(lignes[2][c]!=str(n)): #Arrivée au nombre de sommets
    if (lignes[2][c]!=str(n)):
        n += 1
    if (n==10):
        n = 1
        c += 1
number = ""
while(lignes[2][c]!="]"): #Lecture du nombre de sommets
    number = number + lignes[2][c]
    c += 1
s = int(number) #Nombre de sommets

c = c+4 #arrivée au numéro minimum de couleur
minimum = ""
while(lignes[2][c]!="."): #
    minimum = minimum + lignes[2][c]
    c += 1
min = int(minimum)
max = s - 1 + min #en déduire le numéro maximal de couleur (marquée dans le fichier, mais ça évite d'autres lectures)

arcs = [[0 for j in range(s)] for i in range(s)] #liste de nombres binaires representants les arcs

L = 7 #arrivée à la première ligne dans laquelle on trouve les aretes
c = 0 #on revient à la première colonne
nb = 0
while(L<len(lignes)): #tant qu'on n'est pas à la fin du fichier
    D = 0
    F = 0
    debut = ""
    fin = ""
    if (lignes[L][c-1]=="["): #si on arrive à un crochet de gauche
        while(lignes[L][c]!="]"): #avant le crochet de droite, essayer de relever le sommet de debut
            n = 0
            while((n<10)&(lignes[L][c]!=str(n))):
                n = n+1
            if (lignes[L][c]==str(n)):
                debut = debut + lignes[L][c]
            c += 1 #passage à la colonne suivante
        if (len(debut)>0): #si sommet de debut relevé
            c += 3 + len(id) #arrivée là où est censé être le premier chiffre du sommet de fin
            while(lignes[L][c]!="]"): #avant le crochet de droite, essayer de relever le sommet de fin
                n=0
                while((n<10)&(lignes[L][c]!=str(n))):
                    n = n+1
                if (lignes[L][c]==str(n)):
                    fin = fin + lignes[L][c]
                c += 1 #passage à la colonne suivante
        if ((len(debut)>0)&(len(fin)>0)): #si les sommets de debut et de fin sont effectivement relevés
            D = int(debut) #sommet de debut
            F = int(fin) #sommet de fin
            arcs[D][F]=1 #formation de l'arc DF
            arcs[F][D]=1 #formation de l'arc FD (note : DF = FD)
    c = c+1 #passage à la colonne suivante
    if (c==len(lignes[L])): #si le nombre total d'éléments de la ligne L est dépassée
        c = 0 #on revient à la première colonne
        L = L+1 #on saute une ligne

model = cp_model.CpModel() #initialisation du problème

#initialisation des variables (sommets)
tab = []
for k in range(s):
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
    tab.append(model.new_int_var(min, max, name))

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