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
    C = 7
    var=[P,M,D]
    #Boolean variables
    boolean= []
    for i in range(4):
        boolean.append(model.NewBoolVar(f'{i}'))
    dernier=model.NewBoolVar('dernier')
    # Create the constraints.
    
    #P1 does not work with component D3
    model.Add(P == 1).OnlyEnforceIf(boolean[0])
    model.Add(P != 1).OnlyEnforceIf(boolean[0].Not())
    model.Add(D != 3).OnlyEnforceIf(boolean[0])

    #A processor must have memory that is at least as recent as itself
    model.Add(M >= P)

    
    #The only disk possible with P2 and M2 is disk D2
    for i in range(1,4):

        model.Add(var[i-1] == 2).OnlyEnforceIf(boolean[i])
        model.Add(var[i-1] != 2).OnlyEnforceIf(boolean[i].Not())


   
    model.AddBoolAnd(boolean[1:-1]).OnlyEnforceIf(dernier)
    model.Add(dernier==1).OnlyEnforceIf(boolean[1:-1])


    model.AddImplication(dernier,boolean[3])



    #The total cost of the product must be less than a value C
    model.Add(P+M+D<C)


    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter([P, M, D ])
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    # Solve.
    status = solver.solve(model, solution_printer)
    print(f"Status = {solver.status_name(status)}")
    print(f"Number of solutions found: {solution_printer.solution_count}")


search_for_all_solutions_sample_sat()