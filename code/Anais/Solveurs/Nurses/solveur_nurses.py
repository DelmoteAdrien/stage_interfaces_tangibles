import time, collections, random
from ortools.sat.python import cp_model

#ces deux listes me permettent de nommer les variables
alpha = "abcdefghijklmnopqrstuvwxyz"
Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

nurses = ["Mario","Peach","Luigi","Daisy","Link","Zelda","Bernard","Bianca","Romeo","Juliette","Tristan","Iseult"]

niveaux = [1,2,1,1,0,0,1,0,1,1,2,1]
debutants = []
intermediaires = []
experts = []
for n in range(len(nurses)):
    if (niveaux[n]==0):
        #debutants.append(nurses[n])
        debutants.append(n)
    elif (niveaux[n]==1):
        #intermediaires.append(nurses[n])
        intermediaires.append(n)
    else:
        #experts.append(nurses[n])
        experts.append(n)
competents = experts + intermediaires
ch = "Les debutants sont "
for i in range(len(debutants)):
    ch += nurses[debutants[i]]
    if (i!=len(debutants)-1):
        if (i==len(debutants)-2):
            ch += " et "
        else:
            ch += ", "
print(ch)
print()

ententes = []
deteste = []
for i in range(len(nurses)):
    ententes2 = []
    deteste2 = []
    for j in range(len(nurses)):
        if (((j==i+1)&(i%2==0))|((j==i-1)&(i%2==1))):
            ententes2.append(2)
        else:
            ententes2.append(random.randint(0,2))
            if (ententes2[j]==0):
                deteste2.append(j)
    ententes.append(ententes2)
    deteste.append(deteste2)

for i in range(len(nurses)):
    if (len(deteste[i])>0):
        ch = nurses[i] + " deteste "
        for j in range(len(deteste[i])):
            ch += nurses[deteste[i][j]]
            if (j!=len(deteste[i])-1):
                if (j==len(deteste[i])-2):
                    ch += " et "
                else:
                    ch += ", "
        print(ch)
print()

name_shifts = []
for i in range(7):
    name_shifts2 = []
    for j in range(3):
        name_shifts3 = []
        for k in range(len(nurses)):
            name = ""
            n = k//26
            tab = [n]
            while(n>25):
                n = n//26
                tab.append(n)
            name = name + alpha[tab[len(tab)-1]]
            for l in range(len(tab)-1):
                name = name + alpha[tab[len(tab)-1-l]//(26*(len(tab)-1-l))]
            name = alpha[k%26] + name
            if (j==0):
                name = "D" + str(i+1) + name
            elif (j==1):
                name = "N" + str(i+1) + name
            else:
                name = "LN" + str(i+1) + name
            name_shifts3.append(name)
        name_shifts2.append(name_shifts3)
    name_shifts.append(name_shifts2)

model = cp_model.CpModel() #initialisation du problème

shifts = []
for i in range(7):
    shifts2 = []
    for j in range(3):
        shifts3 = []
        for k in range(len(nurses)):
            shifts3.append(model.new_int_var(0,1,name_shifts[i][j][k]))
        shifts2.append(shifts3)
    shifts.append(shifts2)
a = model.new_bool_var("a")
#b = model.new_bool_var("b")

for i in range(7):
    for j in range(3):
        model.add(sum(shifts[i][j][:])>=1) #les shifts sont tous couverts par au moins une personne

for m in range(len(nurses)):
    #model.add(sum(shifts[:][:][m])>=1) #chaque infirmier couvre au moins 1 shift
    for i in range(7):
        for j in range(3):
            model.add(shifts[i][j][m]==1).only_enforce_if(a)
            model.add(shifts[i][j][m]==0).only_enforce_if(~a)
            for k in range(3):
                if (j!=k):
                    model.add(shifts[i][k][m]==0).only_enforce_if(a) #A nurse does not work the day shift, night shift and late night shift on the same day
            if ((i<6)&(j==2)):
                model.add(shifts[i+1][0][m]==0).only_enforce_if(a) #A nurse does not do a late night shift followed by a day shift the next day.
            if (niveaux[m]==0):
                l = competents[0]
                ind = 0
                while((ententes[m][l]==0)|(ind<=len(competents)-1)):
                    l = competents[ind]
                    ind += 1
                model.add(shifts[i][j][l]==1).only_enforce_if(a)
                for n in range(len(nurses)):
                    if ((n!=l)&(n!=m)&(ententes[m][n]==0)):
                        model.add(shifts[i][j][n]==0).only_enforce_if(a) #Two nurses dislike each other and thus cannot work on the same shift because of that.
            for n in range(len(nurses)):
                if ((n!=m)&(ententes[m][n]==0)):
                    model.add(shifts[i][j][n]==0).only_enforce_if(a) #Two nurses dislike each other and thus cannot work on the same shift because of that.

solver = cp_model.CpSolver() #création d'un solveur du problème
debut = time.perf_counter() #debut de la recherche d'une solution
status = solver.solve(model) #recherche d'une solution
fin = time.perf_counter() #fin de la recherche d'une solution

print("Duree de la recherche d'une solution = ",(fin-debut),"s\n")

def affichage(i,j):
    name = ""
    nb = 1
    while((nb<len(name_shifts[i][j][0]))&(len(name_shifts[i][j][0][nb])!=str(n))):
        n += 1
        if (n==8):
            name += name_shifts[i][j][0][nb]
            nb += 1
            n = 1
    if (len(name_shifts[i][j][0][nb])==str(n)):
        name += name_shifts[i][j][0][nb]
    ch = name + " : "
    S = sum(solver.value(shifts[i][j][:]))
    c = 0
    n = 0
    while((n<len(nurses))&(c<S)):
        if (solver.value(shifts[i][j][n])==1):
            ch += nurses[n]
            if (S>1):
                if (c<S-1):
                    ch += " et "
                elif(c!=S-1):
                    ch += ", "
            c += 1
        n += 1
    return ch

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE: #si le problème est résoluble
    for i in range(7):
        for j in range(3):
            print(affichage(i,j))
else:
    print("Pas de solution trouvee.") #sinon