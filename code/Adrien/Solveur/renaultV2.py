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
def search_for_all_solutions_sample(nbvariable,path):

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
                var= constraint.get("scope").split(' ')

                if all( int(v)<=nbvariable for v in var):
                    
                    #Identify the variables related to the constraints
                    condition=model.NewBoolVar(f'{constraint.get("name")}')
                    intlists=[]
                    intlists2=[]
                    for j in range (len(lists)):
                        list=lists[j].split(' ')
                        intlists.append([int(l) for l in list])
                        intlists2.append([int(l) for l in list[:-1]])
     
                    model.AddAllowedAssignments([dico_variable[v] for v in var],intlists).OnlyEnforceIf(condition)
                    model.AddForbiddenAssignments([dico_variable[v] for v in var[:-1]],intlists2).OnlyEnforceIf(condition.Not())
  



    model.Add(dico_variable['5']==0)
    model.Add(dico_variable['3']==0)
    model.Add(dico_variable['1']==0)
    model.Add(dico_variable['16']==0)
    model.Add(dico_variable['2']==0)
    model.Add(dico_variable['6']==0)
    model.Add(dico_variable['9']==0)
    model.Add(dico_variable['11']==0)
    model.Add(dico_variable['13']==0)
    model.Add(dico_variable['15']==1)
    model.Add(dico_variable['19']==0)
    model.Add(dico_variable['20']==0)

  





    # Create a solver and solve.
    solver = cp_model.CpSolver()
    num_variables = len(model.Proto().variables)
    print(f'Nombre de variables utilisées : {num_variables}')
    
    # Obtenir le nombre de contraintes
    num_constraints = len(model.Proto().variables)
    print(f'Nombre de contraintes : {num_constraints}')

    solution_printer = VarArraySolutionPrinter(  [dico_variable[variable.get('name')] for variable in variables[:nbvariable]] )
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    # Solve.
    status = solver.solve(model, solution_printer)
    print(f"Status = {solver.status_name(status)}")
    print(f"Number of solutions found: {solution_printer.solution_count}")

    


#paramètre : 
# nbvariable: specifies the number of variables, for example, 10 for the first 10 variables.
# path: path to the XML file containing the data.
def search_one_solution_sample(nbvariable,path):


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
            last_conditions=[]
            for constraint in constraints:
                lists= dico_relations[constraint.get("reference")].split('|')   
                var= constraint.get("scope").split(' ')

                if all( int(v)<=nbvariable for v in var):
                    
                    #Identify the variables related to the constraints
                    last_condition=model.NewBoolVar(f'dernier {constraint.get("name")}')
                    intlists=[]
                    for j in range (len(lists)):
                        list=lists[j].split(' ')
                        intlists.append([int(l) for l in list])

                    model.AddAllowedAssignments([dico_variable[v] for v in var],intlists).OnlyEnforceIf(last_condition)
                    model.AddForbiddenAssignments([dico_variable[v] for v in var],intlists).OnlyEnforceIf(last_condition.Not())

                    last_conditions.append(last_condition)

                    model.AddExactlyOne(last_conditions)

          
         
    

    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solver.solve(model)

   

def variable_choisi(nbvariable,path):
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
        dico_variable[variable.get('name')]= int(dico_domain[variable.get('domain')])-1 
    
    dico_max=dico_variable.copy()
    domain_max= []
    for i in range(3):
        valeur_max=max(dico_max.values())

        domain_max.append ([cle for cle, valeur in dico_max.items() if valeur == valeur_max])
        print(f"les {i+1}e variables avec le plus de domaine: {domain_max[i]}")

        for maxi in domain_max[i]:
            dico_max.pop(maxi)


    constraints = root.findall(f".//constraint")


    count= {var: 0 for var in dico_variable }
    constraint_max= []
    for i in range(3):
        if len(count)!=0:
            for c in count:
                for constraint in constraints:
                    var= constraint.get("scope").split(' ')
                    if all( int(v)<=nbvariable for v in var):
                        if var.__contains__(c):
                            count[c]+=1
            valeur_max=max(count.values())
            constraint_max.append([cle for cle, valeur in count.items() if valeur == valeur_max])
            print(f"les {i+1} variable avec le plus de contrainte: {constraint_max[i]}")

            for c in constraint_max[i]:
                count.pop(c)
        
    
    important=[]


    
    


    




variable_choisi(10,'./../renault/megane.xml')


start_time= time.time()
search_for_all_solutions_sample(30,'./../renault/megane.xml')
end_time = time.time()

execution_time= end_time-start_time
print(f"solution :{execution_time}")


'''

print("-----------")

start_time= time.time()
search_one_solution_sample(10,'./../renault/megane.xml')
end_time = time.time()

execution_time= end_time-start_time
print(f"estimation sans contraintes: {execution_time} {execution_time*18000}")'''