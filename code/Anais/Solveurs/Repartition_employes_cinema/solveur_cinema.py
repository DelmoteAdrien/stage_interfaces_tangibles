from constraint import * #importation de la librairie python-constraint
import time

"""
Un extrait de ce lien https://www.artelys.com/app/docs/kalis/3_solveCP.html :
Let suppose that a movie theatre director has to decide in which location each of his employees should be posted.
There are eight employees, named Andrew, David, Jane, Jason, Leslie, Michael, Marilyn and Oliver.
There are four locations: the ticket office, the first entrance, the second entrance and the cloakroom.
These locations require 3, 2, 2, and 1 person respectively.

The variables of the problem are the locations where each employee will work.

There are some constraints associated with this problem:
- each employee must have a unique location;
- Leslie must work at the second entrance;
- Michael must work at the first entrance;
- David, Michael and Jason cannot work together;
- each location must be occupied by exactly the number of employees it requires;
- if David is selling tickets, Marilyn must be with him.

Solving the problem means finding values of the variables satisfying all the constraints.
"""

employes = ["Andrew","David","Jane","Jason","Leslie","Michael","Marilyn","Oliver"] #liste des employés
#A partir de maintenant, on aura : Andrew = 0, David = 1, Jane = 2, Jason = 3, Leslie = 4, Michael = 5, Marilyn = 6 et Oliver = 7
locations = ["le guichet","la premiere entree","la seconde entree","les vestiaires"] #liste des locations
locations2 = [["a","b","c"],["d","e"],["f","g"],["h"]] #liste des places possibles dans ces locations, elles doivent toutes être occupées, ces places serviront de variables

problem = Problem() #initialisation du problème

#initialisation des variables
for i in range(len(locations2)):
    for j in range(len(locations2[i])):
        problem.addVariables(locations2[i][j],range(8)) #each location must be occupied by exactly the number of employees it requires;

#initialisation des contraintes
problem.addConstraint(AllDifferentConstraint()) #each employee must have a unique location
problem.addConstraint(lambda f,g: f==4 or g==4, ("f","g")) #Leslie must work at the second entrance
problem.addConstraint(lambda d,e: d==5 or e==5, ("d","e")) #Michael must work at the first entrance;
for i in range(len(locations2)-1):
    for j in range(len(locations2[i])-1):
        for k in range(j+1,len(locations2[i])):
            #David, Michael and Jason cannot work together;
            problem.addConstraint(lambda l,m: l!=1 or m!=5, (locations2[i][j],locations2[i][k]))
            problem.addConstraint(lambda l,m: l!=3 or m!=5, (locations2[i][j],locations2[i][k]))
            problem.addConstraint(lambda l,m: l!=1 or m!=3, (locations2[i][j],locations2[i][k]))
            #Pour essayer de régler le 1er problème de symétrie constaté
            problem.addConstraint(lambda l,m: l<m, (locations2[i][j],locations2[i][k]))
            if (i==0): #if David is selling tickets, Marilyn must be with him
                problem.addConstraint(lambda l,m: l!=1 or m==6, (locations2[i][j],locations2[i][k]))

debut = time.perf_counter() #debut de la recherche de solutions
solutions = problem.getSolutions() #résolution du problème
fin = time.perf_counter() #fin de la recherche de solutions
print("Durée de la recherche de solutions :",(fin-debut),"s\n") #affichage de la durée de la recherche de solutions

def affichage(num): #fonction pour afficher les employés présents à chaque location dans la solution n°num
    ch = ""
    for ind in range(4):
        ch += "Dans " + locations[ind] + " : "
        for i in range(len(locations2[ind])):
            if ((len(locations2[ind])>1)&(i>0)):
                if (i==len(locations2[ind])-1):
                    ch += " et "
                else:
                    ch += ", "
            ch += affichage2(solutions[num][locations2[ind][i]])
        if (ind<3):   
        	ch += "\n"
    return ch

def affichage2(ind): #fonction pour afficher l'employé associé à l'entier ind
    ch = ""
    if (0 <= ind <= 7):
        ch += employes[ind]
    return ch

#affichage des solutions
for i in range(len(solutions)):
    print("Solution n°",i+1," :")
    print(affichage(i))
    if (i<len(solutions)-1):
    	print()
    	
#Note : plusieurs solutions identiques s'affichent --> problème de symétrie

"""
Exemple de solutions identiques qui s'affichent :
Solution n° 1  :
Dans le guichet : Oliver, Marilyn et Jason
Dans la premiere entree : Michael et Jane
Dans la seconde entree : Leslie et Andrew
Dans les vestiaires : David

Solution n° 3  :
Dans le guichet : Oliver, Marilyn et Jason
Dans la premiere entree : Michael et Jane
Dans la seconde entree : Andrew et Leslie
Dans les vestiaires : David
"""

#Note 2 : On est passé d'une centaine de solutions à 36 solutions, ce qui fait un bon gain de temps

"""
Pour le problème d'ordonnancement des tâches, c'est un cas un peu particulier. Il y a clairement des symétries, mais je ne sais pas encore comment les régler sans trop altérer les tâches.
Peut-être que je pourrais me pencher dessus dans les jours suivants.
"""
