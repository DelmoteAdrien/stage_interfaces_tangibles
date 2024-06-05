from constraint import * #importation de la librairie python-constraint
import time

"""
Rappel de l'exercice 3 du TD d'Algorithmique Avancée sur les problèmes de résolution de contraintes :
On considère le problème d’ordonnancement suivant :
- on a 4 tâches à réaliser de durées 5, 1, 3, 4
- les tâches 2 et 3 ne peuvent être faites en parallèle (mêmes ressources nécessaires), et la 3 doit être faite avant la 4.
On veut savoir si toutes les tâches peuvent être commencées avant le temps t = 7.

Objectif supplémentaire ajouté le mercredi 29 mai : On veut aussi savoir si toutes les tâches peuvent être finies au temps maximum t = 7.
"""

problem = Problem() #initialisation du problème
problem.addVariables("A", range(7)) #initialisation de la première tâche
problem.addVariables("B", range(7)) #initialisation de la deuxième tâche
problem.addVariables("C", range(7)) #initialisation de la troisième tâche
problem.addVariables("D", range(7)) #initialisation de la quatrième tâche

problem.addConstraint(lambda C, D: C + 3 <= D, ("C","D")) #la tâche 3 (de durée 3) doit se faire avant la tâche 4
problem.addConstraint(lambda B, C: (B <= C - 1)|(C + 3 <= B), ("B","C")) #les tâches 2 (de durée 1) et 3 (de durée 3) ne peuvent se faire en parallèle

#fonctions ajoutées pour minimiser la date maximale de fin d'une tâche et faire en sorte que les tâches se finissent en maximum 7 secondes

def fin_max(a,b,c,d): #fonction qui donne la date maximale de fin d'une tâche
    f1 = a + 5 #car la 1ère tâche a comme durée d1 = 5
    f2 = b + 1 #car la 2ème tâche a comme durée d2 = 1
    f3 = c + 3 #car la 3ème tâche a comme durée d3 = 3
    f4 = d + 4 #car la 4ème tâche a comme durée d4 = 4
    return max(f1,f2,f3,f4)

def min_fin_max(a,b,c,d): #fonction permettant de déterminer si la date maximale de fin d'une tâche est inférieure ou égale à 7
    return (fin_max(a,b,c,d) <= 7)

problem.addConstraint(lambda A,B,C,D: min_fin_max(A,B,C,D), ("A","B","C","D")) #ajout de la contrainte de minimisation de la durée max de fin de tâche

debut = time.perf_counter() #debut de la recherche de solutions
solutions = problem.getSolutions() #résolution du problème
fin = time.perf_counter() #fin de la recherche de solutions
print("Durée de la recherche de solutions :",(fin-debut),"s") #affichage de la durée de la recherche de solutions

print("Nombre de solutions : ", len(solutions), "\n")

for i in range(len(solutions)): #affichage des solutions
    print("Solution n°",i+1," :") #affichage du numéro de la solution
    print("debut de la tache A :", solutions[i]["A"]) #affichage du début de la tâche A dans cette solution
    print("debut de la tache B :", solutions[i]["B"]) #affichage du début de la tâche B dans cette solution
    print("debut de la tache C :", solutions[i]["C"]) #affichage du début de la tâche C dans cette solution
    print("debut de la tache D :", solutions[i]["D"]) #affichage du début de la tâche D dans cette solution
    if (i < len(solutions)-1):
        print() #si on n'est pas à la dernière solution, sauter une ligne
