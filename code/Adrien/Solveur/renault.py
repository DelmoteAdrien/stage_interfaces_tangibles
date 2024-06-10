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
        print(self.solution_count)
        for v in self.__variables:
            
            print(f"{v}={self.value(v)}", end=" ")
        print()
    @property
    def solution_count(self) -> int:
        return self.__solution_count

#paramètre : 
# nbvariable: specifies the number of variables, for example, 10 for the first 10 variables.
# path: path to the XML file containing the data.
def search_for_all_solutions_sample_sat(nbvariable,path):


    """ Showcases calling the solver to search for all solutions. """ 
    # Creates the model.
    model = cp_model.CpModel()

    tree = ET.parse(path)
    root = tree.getroot()

    domains = root.findall('.//domain')
    dico_domain={}
    #Retrieve the different domains of the variables from the XML file.
    for domain in domains:
        dico_domain[domain.get('name')]=int(domain.get('nbValues'))



    variables = root.findall('.//variable')
    dico_variable={}
    #Instantiate the variables based on the retrieved domains. 
    for variable in variables[:nbvariable] :
        dico_variable[variable.get('name')]=model.new_int_var(0, int(dico_domain[variable.get('domain')])-1 , variable.get('name'))
 
 


    #Apply the defined constraints to the variables

    #Analyze all relations present in the XML file
    for i in range (nbvariable-1):
        relations = root.findall(f".//relation[@arity='{i}']")
        #If a relation of arity i exists, then apply it to the variables
        if len(relations)>0:

            dico_relations={}
            #Retrieve the relations with an arity of i
            for relation in relations:
                dico_relations[relation.get("name")]= relation.text

            constraints = root.findall(f".//constraint[@arity='{i}']")
            #Get the values of the variables subjected to constraints
            for constraint in constraints:
                lists= dico_relations[constraint.get("reference")].split('|')
                
                #Identify the variables related to the constraints
                for j in range (len(lists)):
                    var= constraint.get("scope").split(' ')
                    if all( int(v)<=nbvariable for v in var):
                        booleans= []
                        #Create booleans for each variable value
                        for k in range (1,i+1):
                            booleans.append(model.NewBoolVar(f"{lists} et {j} et {k} "))
                        #"last_condition" is the final condition: if all booleans are true, then "last_condition" is true.
                        last_condition=model.NewBoolVar('dernier')
                        list=lists[j].split(' ')

                        #Associate the booleans with the variables and their respective values
                        for k in range (i):
                            model.Add(dico_variable[var[k]]==int(list[k])).OnlyEnforceIf(booleans[k])
                            model.Add(dico_variable[var[k]]!=int(list[k])).OnlyEnforceIf(booleans[k].Not())


                        #Verify that if all booleans are true, then "last_condition" is true
                        model.AddBoolAnd(booleans[:-1]).OnlyEnforceIf(last_condition)
                        model.Add(last_condition==1).OnlyEnforceIf(booleans[:-1])
                        model.AddImplication(last_condition,booleans[i-1])

    model.Add(dico_variable['5']==20)


    # Create a solver and solve.
    solver = cp_model.CpSolver()
 

    solution_printer = VarArraySolutionPrinter( [dico_variable[variable.get('name')] for variable in variables[:nbvariable]])
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    # Solve.
    status = solver.solve(model, solution_printer)
    print(f"Status = {solver.status_name(status)}")
    print(f"Number of solutions found: {solution_printer.solution_count}")

start_time= time.time()
search_for_all_solutions_sample_sat(10,'./../renault/megane.xml')
end_time = time.time()

execution_time= end_time-start_time
print(execution_time)