from ortools.sat.python import cp_model


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

    P = model.new_int_var(1, 3 , "Processeur")
    M = model.new_int_var(1, 4 , "Mémoire")
    D = model.new_int_var(1, 3 , "Disque")
    C = 6

    #Boolean variables
    P_is_1 = model.NewBoolVar('P_is_1')
    P_is_2 = model.NewBoolVar('P_is_2')
    M_is_2 = model.NewBoolVar('M_is_2')
    MetP_is_2 = model.NewBoolVar('MetP_is_2')

    # Create the constraints.
    
    #P1 does not work with component D3
    model.Add(P == 1).OnlyEnforceIf(P_is_1)
    model.Add(P != 1).OnlyEnforceIf(P_is_1.Not())
    model.Add(D != 3).OnlyEnforceIf(P_is_1)

    #A processor must have memory that is at least as recent as itself
    model.Add(M >= P)


    #The only disk possible with P2 and M2 is disk D2
    model.Add(P == 2).OnlyEnforceIf(P_is_2)
    model.Add(M==2).OnlyEnforceIf(M_is_2)
    model.Add(P != 2).OnlyEnforceIf(P_is_2.Not())
    model.Add(M!=2).OnlyEnforceIf(M_is_2.Not())
    model.Add(D==2).OnlyEnforceIf(MetP_is_2)
    model.AddBoolAnd(M_is_2,P_is_2).OnlyEnforceIf(MetP_is_2)

    #The total cost of the product must be less than a value C
    model.Add(P+M+D<C)


    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter([P, M, D,P_is_1,MetP_is_2])
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    # Solve.
    status = solver.solve(model, solution_printer)
    print(f"Status = {solver.status_name(status)}")
    print(f"Number of solutions found: {solution_printer.solution_count}")


search_for_all_solutions_sample_sat()