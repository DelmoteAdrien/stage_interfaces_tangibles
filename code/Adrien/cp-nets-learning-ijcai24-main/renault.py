from ortools.sat.python import cp_model
import xml.etree.ElementTree as ET
import time
import sys
import pandas as pd

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
        print(self.solution_count)
        for v in self.__variables:
            
            print(f"{v}={self.value(v)}")
        print()
    @property
    def solution_count(self) -> int:
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
    tree = ET.parse("renault/"+path+".xml")
    root = tree.getroot()

    #Retrieve the different domains of the variables from the XML file.
    dict_domain = { domain.get('name'): [int(element) for element in domain.text.split() if element != "\n"] 
                   for domain in root.findall('.//domain') 
                   }
    #Instantiate the variables based on the retrieved domains.

    df = pd.read_csv("datasets/renault_"+path+".csv")
    dict_variable = {
        variable.get('name'): model.NewIntVarFromDomain(
            cp_model.Domain.FromValues(dict_domain[variable.get('domain')]),
            variable.get('name'))
        for variable in root.findall('.//variable') if variable.get('name') in df.columns.tolist()
        }
    print(dict_variable)

    
    #Apply the defined constraints to the variables

    #Analyze all relations present in the XML file
    for i in range (len(dict_variable)):
        relations = {
            relation.get("name"): relation.text
            for relation in root.findall(f".//relation[@arity='{i}']")
        }
        

        #Get the values of the variables subjected to constraints
        for constraint in root.findall(f".//constraint[@arity='{i}']"):
            scope= constraint.get("scope").split(' ')
            
            if all(variable in dict_variable for variable in scope):
                tuples= relations[constraint.get("reference")].split('|')   
            
                #Identify the variables related to the constraints

                intlists = [
                    [int(value) for value in tuple.split(' ') if isint(value)]
                    for tuple in tuples
                ]
           
                model.AddAllowedAssignments([dict_variable[var] for var in scope],intlists)
            
    
    for var,value in assign_value.items():
        model.Add(dict_variable[var]==value)
  
        
    # Create a solver and solve.
    solver = cp_model.CpSolver()
    num_variables = len(model.Proto().variables)
    print(f'Nombre de variables utilisées : {num_variables}')
    
    # Obtenir le nombre de contraintes
    num_constraints = len(model.Proto().variables)
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
    tree = ET.parse("renault/"+path+".xml")
    root = tree.getroot()

    #Retrieve the different domains of the variables from the XML fil
    dict_domain = {
        domain.get('name'): [int(element) for element in domain.text.split() if element != "\n"]
        for domain in root.findall('.//domain')
    }


    #Instantiate the variables based on the retrieved domains. 
    df = pd.read_csv("datasets/renault_"+path+".csv")
    dict_variable = {
        variable.get('name'): dict_domain[variable.get('domain')]
        for variable in root.findall('.//variable') if variable.get('name') in df.columns.tolist()
    }




    constraints = root.findall(f".//constraint")
    
    assign_value={}
 
    possible_values={var: [str(i) for i in domain] for var,domain in dict_variable.items() }
 
    
    while True: 
        while True:
            comparaison={var: [] for var in dict_variable }

            for constraint in constraints:
                variable_constraint= constraint.get("scope").split(' ')
                if all(variable in dict_variable for variable in variable_constraint):
                    positions=[(variable_constraint.index(value),assign_value[value]) for value in assign_value if value in variable_constraint]                    
                    reference=constraint.get("reference")
                    relation = root.findall(f".//relation[@name='{reference}']")
                    tuples= relation[0].text.split('|')

                    for tuple in tuples:
                        tuple=tuple.split(' ')
                        tuple=[element for element in tuple if isint(element)]

                        if positions:
                            if all( tuple[index]== str(valeur) for index,valeur in positions):
                                for variable in variable_constraint:
                                        if variable not in assign_value and tuple[variable_constraint.index(variable)] not in comparaison[variable]:
                                           comparaison[variable].append(tuple[variable_constraint.index(variable)])  

                        else:
                            for variable in variable_constraint:
                                    if variable not in assign_value and tuple[variable_constraint.index(variable)] not in comparaison[variable]: 
                                        comparaison[variable].append(tuple[variable_constraint.index(variable)])  

                    for variable in variable_constraint:
                        if variable in possible_values:  
                            possible_values[variable]= [valeur for valeur in comparaison[variable] if valeur in possible_values[variable]]
                            comparaison[variable]=[]



            for value in possible_values.values():
                if (len(value)==0):
                    print("Erreur: une des variables a une taille de domaine de 0")
                    sys.exit(1)

            change=False
            possible_value_copy=possible_values.copy()

            for variable,value in possible_value_copy.items():    
                if len(value)==1:
                    change=True
                    assign_value[variable]=int(value[0])
                    possible_values.pop(variable)

            if not change:
                break


        max_length=max([len(variable) for variable in possible_values.values()])
        max_domain_variable=[cle for cle, value in possible_values.items() if len(value) == max_length]


        produit=1
        for valeur in possible_values.values():
            produit *= len(valeur)
        combination=produit
        print("Combinaison : "+str(combination))
        print(" ")

        if combination < 10000:
            break

        count= {var: 0 for var in dict_variable }


        for c in count:
            for constraint in constraints:
                variable_constraint = constraint.get("scope").split()
                if c in variable_constraint:
                    positions = [(variable_constraint.index(variable), assign_value[variable]) for variable in assign_value if variable in variable_constraint]
                    reference = constraint.get("reference")
                    relation = root.find(f".//relation[@name='{reference}']")
                    tuples = relation.text.split('|')

                    if positions:
                        for tuple in tuples:
                            tuple = tuple.split()
                            if all(tuple[index] == str(valeur) for index, valeur in positions):
                                count[c] += 1
                    else:
                        count[c] += int(relation.get("nbTuples"))


        max_count=max(count.values())
        max_constraint=[cle for cle, valeur in count.items() if valeur == max_count]
        
        change=False
        for variable in max_domain_variable:
            if variable in max_constraint:
                change=True
                assign_value[variable]=int(input("choisir une valeur pour "+variable+" elle doit prendre un de ces nombres :"+ str(possible_values[variable]) + ": "))
                print(" ")
                max_domain_variable.remove(variable)
                possible_values.pop(variable)

        if not change:
            variable = max_domain_variable[0]
            assign_value[variable]=int(input("choisir une valeur pour "+variable+" elle doit prendre ces nombres :"+ str(possible_values[variable]) + ": "))   
            print(" ")
            possible_values.pop(variable)
        
                

    return assign_value



