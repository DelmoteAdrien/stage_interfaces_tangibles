from ortools.sat.python import cp_model
import xml.etree.ElementTree as ET
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


    """ Showcases calling the solver to search for all solutions. """ 
    # Creates the model.
    model = cp_model.CpModel()

    tree = ET.parse('./../renault/megane.xml')
    root = tree.getroot()

    nbvariable=10

    domains = root.findall('.//domain')
    dico_domaine={}
    for domain in domains:
        dico_domaine[domain.get('name')]=int(domain.get('nbValues'))



    variables = root.findall('.//variable')
    dico_variable={}
    for i in range(nbvariable):
        variable= variables[i]
        dico_variable[variable.get('name')]=model.new_int_var(0, int(dico_domaine[variable.get('domain')])-1 , variable.get('name'))
 



    for i in range (nbvariable+1):
        relations = root.findall(f".//relation[@arity='{i}']")
        if len(relations)>0:
            dico_relations={}
            for relation in relations:
                dico_relations[relation.get("name")]= relation.text


            constraints = root.findall(f".//constraint[@arity='{i}']")


            for constraint in constraints:
                lists= dico_relations[constraint.get("reference")].split('|')
                
                for j in range (len(lists)):
                    var= constraint.get("scope").split(' ')
                    if (len(var)>2):
                        print(f"{all( int(v)<=nbvariable for v in var)} et {var}")
                    if all( int(v)<=nbvariable for v in var):
                        choix= []
                        for k in range (1,i+1):
                            choix.append(model.NewBoolVar(f"{lists} et {j} et {k} "))
                        list=lists[j].split(' ')
                        for k in range (i-1):
                            model.add(dico_variable[var[k]]!=int(list[k])).OnlyEnforceIf(choix[k].Not())
                            model.add(dico_variable[var[k]]==int(list[k])).OnlyEnforceIf(choix[k])
    
                        model.AddBoolAnd(choix[:-1]).OnlyEnforceIf(choix[i-1])
                        model.add(dico_variable[var[i-1]]==int(list[i-1])).OnlyEnforceIf(choix[i-1])
            model.add(dico_variable['1']==1)
            model.add(dico_variable['5']==12)
    # Create a solver and solve.
    solver = cp_model.CpSolver()
 
 
    solution_printer = VarArraySolutionPrinter([dico_variable[str(i+1)] for i in range(nbvariable)])
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