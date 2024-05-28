from constraint import * #importation de la librairie python-constraint
import time

"""
Rappel de l'exercice 3 du TD d'Algorithmique Avancée sur les problèmes de résolution de contraintes :
On considère le problème d’ordonnancement suivant :
- on a 4 tâches à réaliser de durées 5, 1, 3, 4
- les tâches 2 et 3 ne peuvent être faites en parallèle (mêmes ressources nécessaires), et la 3 doit
être faite avant la 4.
On veut savoir si toutes les tâches peuvent être commencées avant le temps t = 7.
"""

problem = Problem() #initialisation du problème
problem.addVariables("A", range(7)) #initialisation de la première tâche
problem.addVariables("B", range(7)) #initialisation de la deuxième tâche
problem.addVariables("C", range(7)) #initialisation de la troisième tâche
problem.addVariables("D", range(7)) #initialisation de la quatrième tâche

problem.addConstraint(lambda C, D: C + 3 <= D, ("C","D")) #la tâche 3 (de durée 3) doit se faire avant la tâche 4
problem.addConstraint(lambda B, C: (B <= C - 1)|(C + 3 <= B), ("B","C")) #les tâches 2 (de durée 1) et 3 (de durée 3) ne peuvent se faire en parallèle
debut = time.perf_counter() #debut de la recherche de solutions
solutions = problem.getSolutions() #résolution du problème
fin = time.perf_counter() #fin de la recherche de solutions
print("Durée de la recherche de solutions :",(fin-debut),"s\n") #affichage de la durée de la recherche de solutions
for i in range(len(solutions)): #affichage des solutions
    print("Solution n°",i+1," :") #affichage du numéro de la solution
    print("debut de la tache A :", solutions[i]["A"]) #affichage du début de la tâche A dans cette solution
    print("debut de la tache B :", solutions[i]["B"]) #affichage du début de la tâche B dans cette solution
    print("debut de la tache C :", solutions[i]["C"]) #affichage du début de la tâche C dans cette solution
    print("debut de la tache D :", solutions[i]["D"]) #affichage du début de la tâche D dans cette solution
    if (i < len(solutions)-1):
        print() #si on n'est pas à la dernière solution, sauter une ligne

#note : Est-ce que je devrais aussi essayer de minimiser le début maximal d'une tâche ?
