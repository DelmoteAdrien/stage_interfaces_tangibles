from ortools.sat.python import cp_model
import xml.etree.ElementTree as ET
import time
import sys


def isint(element):
    """
    Vérifie si une valeur donnée peut être convertie en entier.

    Args:
        valeur (str): La chaîne de caractères à vérifier.

    Returns:
        bool: True si la valeur peut être convertie en entier, False sinon.
    """
    try:
        int(element)  # Tente de convertir la chaîne en float
        return True
    except ValueError:
        return False
    
class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables: list[cp_model.IntVar]):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self) -> None:
        self.__solution_count += 1
        #if self.solution_count==31104:
        #    end_time = time.time()

        #    execution_time= end_time-start_time
        #    print("combinaison :", self.solution_count)
        #    print("time: ", execution_time)
        #    sys.exit()



        print(self.solution_count)
        #for v in self.__variables:
            
            #print(f"{v}={self.value(v)}")
        #print()

    @property
    def solution_count(self) -> int:
        for v in self.__variables:
            
            print(f"{v}={self.value(v)}")
        return self.__solution_count


#paramètre : 
# nbvariable: specifies the number of variables, for example, 10 for the first 10 variables.
# path: path to the XML file containing the data.
def search_for_all_solutions_sample(path,assign_value):

    """
    Montre comment appeler le solveur pour rechercher toutes les solutions.

    Args:
        path (str): Le chemin vers le fichier XML contenant les variables et les contraintes.
        affectation (dict): Un dictionnaire de contraintes supplémentaires à appliquer aux variables.
    """

    """ Showcases calling the solver to search for all solutions. """ 
    # Creates the model.
    model = cp_model.CpModel()

    # Parse le fichier XML.
    tree = ET.parse(path)
    root = tree.getroot()

    #Retrieve the different domains of the variables from the XML file.
    dict_domain = { domain.get('name'): [element.strip('"') for element in domain.text.split() if element != "\n"] 
                   for domain in root.findall('.//domain') 
                   }
    
    
    dict_domain_index= { domain.get('name'): [i for i in range(len(domain.text.split())) if domain.text.split()[i] != "\n"] 
                   for domain in root.findall('.//domain') 
                   }

    #Instantiate the variables based on the retrieved domains. 
    dict_variable = {
        variable.get('name'): model.NewIntVarFromDomain(
            cp_model.Domain.FromValues(dict_domain_index[variable.get('domain')]),
            variable.get('name'))
        for variable in root.findall('.//variable')
    }
    
    #Apply the defined constraints to the variables

    #Analyze all relations present in the XML file

       
    relations = {
            relation.get("name"): relation.text
            for relation in root.findall(f".//relation")
        }
        

    #Get the values of the variables subjected to constraints
    for constraint in root.findall(f".//constraint"):

            scope= constraint.get("scope").split(' ')
            tuples= relations[constraint.get("reference")].split('|')   
            
            #Identify the variables related to the constraints
            intlists = [
                [value.strip('\n') for value in tuple.split()]
                for tuple in tuples
                ]
 
            intlists_index = [
                [
                    dict_domain[root.find(f".//variable[@name='{scope[j]}']").get("domain")].index(value)
                    for j, value in enumerate(intlist)
                    ]
                    for intlist in intlists
                    ]
            model.AddAllowedAssignments([dict_variable[var] for var in scope],intlists_index)
            

    for var,value in assign_value.items():
        model.Add(dict_variable[var]==dict_domain[root.find(f".//variable[@name='{var}']").get("domain")].index(value))
  

    # Create a solver and solve.
    solver = cp_model.CpSolver()
    num_variables = len(model.Proto().variables)
    print(f'Nombre de variables utilisées : {num_variables}')
    
    # Obtenir le nombre de contraintes
    num_constraints = len(model.Proto().constraints)
    print(f'Nombre de contraintes : {num_constraints}')

    solution_printer = VarArraySolutionPrinter(  [dict_variable[variable] for variable in dict_variable] )
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    # Solve.
    status = solver.solve(model, solution_printer)
    print(f"Status = {solver.status_name(status)}")
    print(f"Number of solutions found: {solution_printer.solution_count}")


def variable_choisi(path):
    """
    Sélectionne les valeurs des variables en fonction des domaines et des contraintes définis dans un fichier XML.

    Args:
        path (str): Le chemin vers le fichier XML contenant les variables et les contraintes.

    Returns:
        dict: Un dictionnaire contenant les variables et leurs valeurs choisies.
    """
    # Parse le fichier XML
    tree = ET.parse(path)
    root = tree.getroot()

    #Retrieve the different domains of the variables from the XML file.
    dict_domain = { domain.get('name'): [element.strip('"') for element in domain.text.split() if element != "\n"] 
                   for domain in root.findall('.//domain') 
                   }
 
    #Instantiate the variables based on the retrieved domains. 
    dict_variable = {
        variable.get('name'): dict_domain[variable.get('domain')]
        for variable in root.findall('.//variable')
    }

       
    constraints = root.findall(f".//constraint")
    
    assign_value={}
 
    possible_values={var: [str(i) for i in domain] for var,domain in dict_variable.items() }
    
 
    
    while True: 
        #To change domains
        while True:
            #comparison compares the possible values in the constraint with the values in possible values
            comparison={var: [] for var in dict_variable }

            for constraint in constraints:
                #data processing
                variable_constraint= constraint.get("scope").split(' ')
                positions=[(variable_constraint.index(value),assign_value[value]) for value in assign_value if value in variable_constraint]                    
                reference=constraint.get("reference")
                relation = root.findall(f".//relation[@name='{reference}']")
                tuples= relation[0].text.split('|')

                for tuple in tuples:
                    tuple=tuple.split()


                    #if positions are not empty (and therefore if there are variables assigned in this constraint)
                    if positions:
                        #Takes only tuples that respect the assigned variable combination 
                        if all( tuple[index]== str(valeur) for index,valeur in positions):
                            for variable in variable_constraint:
                                    #retrieves possible values for variables not already assigned 
                                    if variable not in assign_value and tuple[variable_constraint.index(variable)] not in comparison[variable]:
                                       comparison[variable].append(tuple[variable_constraint.index(variable)])  

                    else:
                        for variable in variable_constraint:
                                #retrieves the possible values of variables that are not already assigned to all tuples 
                                if variable not in assign_value and tuple[variable_constraint.index(variable)] not in comparison[variable]: 
                                        comparison[variable].append(tuple[variable_constraint.index(variable)])  
                #Remove values not in tuples (comparison)
                for variable in variable_constraint:
                    if variable in possible_values:  
                        possible_values[variable]= [valeur for valeur in comparison[variable] if valeur in possible_values[variable]]
                        comparison[variable]=[]


            change=False
            possible_value_copy=possible_values.copy()
            #Assign variables that have only one possible value and start over if this is the case (as this will modify the domains of other variables).
            for variable,value in possible_value_copy.items():    
                if len(value)==1:
                    change=True
                    assign_value[variable]=value[0]
                    possible_values.pop(variable)
            if not change:
                break

        #Recovers variables with the largest domain
        max_length=max([len(variable) for variable in possible_values.values()])
        max_domain_variable=[cle for cle, value in possible_values.items() if len(value) == max_length]

        #Cartesian product of domains to find the number of combinations
        produit=1
        for valeur in possible_values.values():
            produit *= len(valeur)
        combination=produit
        print("Combinaison : "+str(combination))
        print(" ")

        if combination < 20000:
            break

        #Look at the variables in the most constrained (tuples)
        count= {var: 0 for var in dict_variable }

        for c in count:
            for constraint in constraints:
                #data processing
                variable_constraint = constraint.get("scope").split()
                if c in variable_constraint:
                    positions = [(variable_constraint.index(variable), assign_value[variable]) for variable in assign_value if variable in variable_constraint]
                    reference = constraint.get("reference")
                    relation = root.find(f".//relation[@name='{reference}']")
                    tuples = relation.text.split('|')
                    #if positions are not empty (and therefore if there are variables assigned in this constraint)
                    if positions:
                        for tuple in tuples:
                            tuple = tuple.split()
                            #Takes only tuples that respect the assigned variable combination 
                            if all(tuple[index] == str(valeur) for index, valeur in positions):
                                count[c] += 1
                    else:
                        #retrieves the possible values of variables that are not already assigned to all tuples
                        count[c] += int(relation.get("nbTuples"))

        #Takes value in most constraint
        max_count=max(count.values())
        max_constraint=[cle for cle, valeur in count.items() if valeur == max_count]
        
        #Asks user to assign a variable
        change=False
        for variable in max_domain_variable:
            #If a variable is both in the most constraint and in the largest domain
            if variable in max_constraint:
                change=True
                assign_value[variable]=input("choisir une valeur pour "+variable+" elle doit prendre un de ces nombres :"+ str(possible_values[variable]) + ": ")
                print(" ")
                max_domain_variable.remove(variable)
                possible_values.pop(variable)
        #If a variable is not both in the strongest constraint and in the widest domain, only the variables with the widest domain are taken.
        if not change:
            variable = max_domain_variable[0]
            assign_value[variable]= input("choisir une valeur pour "+variable+" elle doit prendre ces nombres :"+ str(possible_values[variable]) + ": ")
            print(" ")
            possible_values.pop(variable)
        
                

    return assign_value

#path= './../renault/small.xml'
path = './../souffleuse/souffleuse_CSP.xml'
assign_value= variable_choisi(path)



start_time= time.time()
search_for_all_solutions_sample(path,assign_value)
end_time = time.time()

execution_time= end_time-start_time
print("time: ", execution_time)