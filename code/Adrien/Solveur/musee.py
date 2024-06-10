from ortools.sat.python import cp_model
import time

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables: list[cp_model.IntVar]):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self) -> None:
        self.__solution_count += 1
        for v in self.__variables:
            print(f"{v}={self.value(v)}", end=" ")
        print()

    @property
    def solution_count(self) -> int:
        return self.__solution_count


def search_for_all_solutions_sample_sat():
    """Showcases calling the solver to search for all solutions."""
    # Creates the model.
    model = cp_model.CpModel()

    # Creates the variables.
    Nombre = model.new_int_var(1, 3 , "Nombre")
    Age = model.new_int_var(1, 4 , "Age")
    Xp = model.new_int_var(1, 2 , "Xp")
    Humeur = model.new_int_var(1, 3 , "Humeur")
    Handicap= model.new_int_var(1, 4 , "Handicap")
    Duree= model.new_int_var(1, 3 , "Durée")
   

    # Boolean variable
    Age_is_1 = model.NewBoolVar('age_is_1')
    Age_is_2 = model.NewBoolVar('age_is_2')
    Age_is_4 = model.NewBoolVar('age_is_4')
    Handicap_is_1 = model.NewBoolVar('Handicap_is_1')
    Handicap_is_2 = model.NewBoolVar('Handicap_is_2')
    # Create the constraints.

    #Constraints for age

    #Associate the Boolean variable with the CSP variable
    model.add(Age!=1).OnlyEnforceIf(Age_is_1.Not())
    model.add(Age==1).OnlyEnforceIf(Age_is_1)
    model.add(Age!=2).OnlyEnforceIf(Age_is_2.Not())
    model.add(Age==2).OnlyEnforceIf(Age_is_2)
    model.add(Age!=4).OnlyEnforceIf(Age_is_4.Not())
    model.add(Age==4).OnlyEnforceIf(Age_is_4)

    #Constraints for nombre

    #Children under the age of 13 are not allowed to go on the course alone.
    model.add(Nombre!=1).OnlyEnforceIf(Age_is_1)
    model.add(Nombre!=1).OnlyEnforceIf(Age_is_2)

    #People with cognitive disabilities must be in a group of at least 3 people
    model.add(Nombre==3).OnlyEnforceIf(Handicap_is_2)

    #Contraintes pour Xp
    #The advanced experience is reserved for adults
    model.add(Xp!=2).OnlyEnforceIf(Age_is_4.Not())
    #People with cognitive disabilities cannot participate in the experimental course.
    model.add(Xp!=2).OnlyEnforceIf(Handicap_is_2)


    #Contraintes pour Duree
    #Only adults can participate in the 1h30 course.
    model.add(Duree!=3).OnlyEnforceIf(Age_is_4.Not())
    #Individuals with disabilities are not allowed to participate in the 1h30 course
    model.add(Duree!=3).OnlyEnforceIf(Handicap_is_1.Not())

    #Contraintes pour Handicap
    #Associate the Boolean variable with the CSP variable
    model.add(Handicap!=1).OnlyEnforceIf(Handicap_is_1.Not())
    model.add(Handicap==1).OnlyEnforceIf(Handicap_is_1)
    model.add(Handicap!=2).OnlyEnforceIf(Handicap_is_2.Not())
    model.add(Handicap==2).OnlyEnforceIf(Handicap_is_2)

    #Children with cognitive issues cannot participate in the course.
    model.add(Handicap!=2).OnlyEnforceIf(Age_is_4.Not())
    

    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter([Nombre, Age, Xp,Humeur,Handicap,Duree])
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    # Solve.
    status = solver.solve(model, solution_printer)
    print(f"Status = {solver.status_name(status)}")
    print(f"Number of solutions found: {solution_printer.solution_count}")


start_time= time.time()
search_for_all_solutions_sample_sat()
end_time = time.time()

execution_time= end_time-start_time
print(execution_time)