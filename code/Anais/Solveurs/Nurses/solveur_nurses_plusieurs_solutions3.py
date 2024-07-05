"""Example of a simple nurse scheduling problem."""
from ortools.sat.python import cp_model
import time


def main() -> None:
    alpha = "abcdefghijklmnopqrstuvwxyz"
    Alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    jours = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]

    # Data.
    num_nurses = 3
    num_shifts = 1
    num_days = 7
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)

    print("Nombre d'infirmiers : ", num_nurses)
    print("Nombre de jours : ", num_days)
    print("Nombre de services par jour : ", num_shifts)
    print()

    #implémentation nombres minimal et maximal de jours consécutifs de travail
    nombre_shifts_consecutifs = [[3,5],[2,3],[2,4]]
    
    #implémentation nombre minimal de jours de repos
    nombre_minimal_repos = [2,2,3]

    #implémentation jours de repos déjà décidés
    services_repos_deja_decides = [
        [
            [],[],[],[],[],[],[]
        ],
        [
            [],[],[],[],[],[0,1,2],[]
        ],
        [
            [0,1,2],[],[],[],[],[0,1,2],[]
        ],
    ]

    # Creates the model.
    model = cp_model.CpModel()

    #initialisation des variables (shifts) basée sur le code dans le lien
    names = []
    shifts = []
    for n in all_nurses:
        shifts2 = []
        for d in all_days:
            shifts3 = []
            for s in all_shifts:
                name = ""
                m = n//26
                if (m>0):
                    tab2 = [m]
                    while(m>25):
                        m = m//26
                        tab2.append(m)
                    name = name + alpha[tab2[len(tab2)-1]]
                    for l in range(len(tab2)-1):
                        name = name + alpha[tab2[len(tab2)-1-l]//(26*(len(tab2)-1-l))]
                    name = Alpha[m%26] + name
                    if ((d==0)&(s==0)):
                        names.append(name)
                    name += str(d+1)
                    if (num_shifts>1):
                        name += "_" + str(s+1)
                else:
                    name = Alpha[n]
                    if ((d==0)&(s==0)):
                        names.append(name)
                    name += str(s+1)
                    if (num_shifts>1):
                        name += "_" + str(s+1)
                shifts3.append(model.new_int_var(0,1,name))
            shifts2.append(shifts3)
        shifts.append(shifts2)

    #initialisation des contraintes
    for n in all_nurses: #shifts de travail et de repos
        shifts_travailles = []
        for d in all_days:
            for s in all_shifts:
                if s in services_repos_deja_decides[n][d]: #si on tombe sur un shift de repos déjà décidé
                    model.add(shifts[n][d][s] == 0)
                shifts_travailles.append(shifts[n][d][s])
        model.add(nombre_shifts_consecutifs[n][0] <= sum(shifts_travailles))
        model.add(sum(shifts_travailles) <= nombre_shifts_consecutifs[n][1])
        model.add(nombre_minimal_repos[n] <= num_days*num_shifts - sum(shifts_travailles))

    for d in all_days: #au moins un infirmier par shift
        for s in all_shifts:
            shifts_occupes = []
            for n in all_nurses:
                shifts_occupes.append(shifts[n][d][s])
            model.add(1 <= sum(shifts_occupes))

    #Les infirmiers ont un nombre minimal et maximal de jours consécutifs
    for n in all_nurses:
        #shifts_travail = [[False*num_shifts]*num_days]
        C1 = nombre_shifts_consecutifs[n][0]
        C2 = nombre_shifts_consecutifs[n][1]
        d = 0
        s = 0
        while (d < num_days):
            d2 = d
            s2 = s
            D = d2*(s2+1) - d*(s+1)
            shifts_worked = []
            while ((d2 < num_days)&(D < C1)&(s2 not in services_repos_deja_decides[n][d2])):
                shifts_worked.append(shifts[n][d][s])
                if (s2 == len(all_shifts) - 1):
                    s2 = 0
                    d2 += 1
                else:
                    s2 += 1
                D = d2*(s2+1) - d*(s+1)
            if (len(shifts_worked) == C1):
                model.add(sum(shifts_worked) == C1)
                if (s2 == len(all_shifts) - 1):
                    s2 = 0
                    d2 += 1
                else:
                    s2 += 1
            elif (s == len(all_shifts) - 1):
                s = 0
                d += 1
            else:
                s += 1

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True

    class NursesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""

        def __init__(self, shifts, num_nurses, num_days, num_shifts, limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shifts = shifts
            self._num_nurses = num_nurses
            self._num_days = num_days
            self._num_shifts = num_shifts
            self._solution_count = 0
            self._solution_limit = limit

        def on_solution_callback(self):
            self._solution_count += 1
            if (self._solution_count<=self._solution_limit):
                print(f"Solution {self._solution_count}")
            nurses = []
            for d in range(self._num_days):
                nurses2 = []
                for s in range(self._num_shifts):
                    nurses3 = []
                    for n in range(self._num_nurses):
                        if (self.value(self._shifts[n][d][s])==1):
                            nurses3.append(n)
                    nurses2.append(nurses3)
                nurses.append(nurses2)
            for d in range(self._num_days):
                for s in range(self._num_shifts):
                    j = d%7
                    ch = ""
                    ch += jours[j]
                    if (self._num_days > 7):
                        i = d//7+1
                        ch += str(i)
                    if (self._num_shifts > 1):
                        ch += "_" + str(s+1)
                    ch += " : "
                    for n in nurses[d][s]:
                        #print("n = ",n)
                        ch += names[n]
                        if (len(nurses[d][s])>1):
                            if (nurses[d][s].index(n)<len(nurses[d][s])-2):
                                ch += ", "
                            elif (nurses[d][s].index(n)==len(nurses[d][s])-2):
                                ch += " et "
                    if (self._solution_count<=self._solution_limit):
                        print(ch)
            """
            for d in range(self._num_days):
                if (self._solution_count<=self._solution_limit):
                    print(f"Day {d}")
                for n in range(self._num_nurses):
                    is_working = False
                    for s in range(self._num_shifts):
                        if self.value(self._shifts[(n, d, s)]):
                            is_working = True
                            if (self._solution_count<=self._solution_limit):
                                print(f"  Nurse {n} works shift {s}")
                    if not is_working:
                        if (self._solution_count<=self._solution_limit):
                            print(f"  Nurse {n} does not work")
            if (self._solution_count<=self._solution_limit):
                print()
            """
            """
            else:
                print(f"Solution {self._solution_count} non affichee")
            """
            """
            if self._solution_count >= self._solution_limit:
                print(f"Stop search after {self._solution_limit} solutions")
                self.stop_search()
            """

        def solutionCount(self):
            return self._solution_count

    # Display the first solution.
    solution_limit = 1
    solution_printer = NursesPartialSolutionPrinter(
        shifts, num_nurses, num_days, num_shifts, solution_limit
    )

    debut = time.perf_counter()
    solver.solve(model, solution_printer)
    fin = time.perf_counter()
    duree = fin - debut

    ch1 = "solutions found"
    l1 = len(ch1)
    ch2 = "search time"
    l2 = len(ch2)

    # Statistics.
    print("\nStatistics")
    print(f"  - conflicts      : {solver.num_conflicts}")
    print(f"  - branches       : {solver.num_branches}")
    print("  - search time", (l1-l2-2)*" ",":",duree, "s")
    print(f"  - wall time      : {solver.wall_time} s")
    print(f"  - solutions found: {solution_printer.solutionCount()}")


if __name__ == "__main__":
    main()