"""Example of a simple nurse scheduling problem."""
from ortools.sat.python import cp_model
import time


def main() -> None:
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
    """

    """
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

    # Creates shift variables.
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.new_bool_var(f"shift_n{n}_d{d}_s{s}")

    # Each shift is assigned to exactly one nurse in the schedule period.
    for d in all_days:
        for s in all_shifts:
            model.add_exactly_one(shifts[(n, d, s)] for n in all_nurses)

    # Each nurse works at most one shift per day.
    for n in all_nurses:
        for d in all_days:
            model.add_at_most_one(shifts[(n, d, s)] for s in all_shifts)

    # Try to distribute the shifts evenly, so that each nurse works
    # min_shifts_per_nurse shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of nurses, some nurses will
    # be assigned one more shift.
    min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
    if num_shifts * num_days % num_nurses == 0:
        max_shifts_per_nurse = min_shifts_per_nurse
    else:
        max_shifts_per_nurse = min_shifts_per_nurse + 1
    for n in all_nurses:
        shifts_worked = []
        for d in all_days:
            for s in all_shifts:
                shifts_worked.append(shifts[(n, d, s)])
        #Définition d'un encadrement du nombre de quarts de travail des infirmiers
        #pour répartition équitable
        model.add(min_shifts_per_nurse <= sum(shifts_worked))
        model.add(sum(shifts_worked) <= max_shifts_per_nurse)
        #Définition d'un encadrement du nombre de quarts de travail des infirmiers
        #selon jour minimal de repos
        model.add(nombre_minimal_repos[n] <= sum(shifts_worked))
        model.add(sum(shifts_worked) <= (num_shifts * num_days) - nombre_minimal_repos[n])

    #Les infirmiers ne travaillent pas durant les jours de repos assignés
    for n in all_nurses:
        for d in all_days:
            if (len(services_repos_deja_decides[n][d])>0):
                repos = []
                for s in services_repos_deja_decides[n][d]:
                    if s in all_shifts:
                        repos.append(shifts[(n, d, s)])
                model.add(sum(repos) == 0)

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
                shifts_worked.append(shifts[(n, d2, s2)])
                if (s2 == len(all_shifts) - 1):
                    s2 = 0
                    d2 += 1
                else:
                    s2 += 1
                D = d2*(s2+1) - d*(s+1)
            if (len(shifts_worked) == C1):
                model.add(sum(shifts_worked) == C1)
                """
                shifts_worked2 = []
                shifts_worked2[0::(C1-1)] = shifts_worked
                while ((d2 < num_days)&(D < C2)&(s2 not in services_repos_deja_decides[n][d2])):
                    if (s2 == len(all_shifts) - 1):
                        s2 = 0
                        d2 += 1
                    else:
                        s2 += 1
                    D = d2*(s2+1) - d*(s+1)
                model.add(sum(shifts_worked2) <= C2)
                """
                if (s2 == len(all_shifts) - 1):
                    s2 = 0
                    d2 += 1
                else:
                    s2 += 1
                """
                shifts_worked2 = []
                shifts_worked2[0::(C1-1)] = shifts_worked
                d3 = d2
                s3 = s2
                D = d3*(s3+1) - d*(s+1)
                while ((d3 < num_days)&(D < C2 + 1)&(s3 not in services_repos_deja_decides[n][d2])):
                    shifts_worked2.append(shifts[(n, d3, s3)])
                    model.add(sum(shifts_worked2) <= D)
                    if (s3 == len(all_shifts) - 1):
                        s3 = 0
                        d3 += 1
                    else:
                        s3 += 1
                    D = d3*(s3+1) - d*(s+1)
                if (len(shifts_worked2) == C2 + 1):
                    model.add(sum(shifts_worked2) <= C2)
                    if (s3 == len(all_shifts) - 1):
                        s = 0
                        d = d3 + 1
                    else:
                        s = s3 + 1
                        d = d3
                elif (s2 == len(all_shifts) - 1):
                    s = 0
                    d = d2 + 1
                else:
                    s = s2 + 1
                    d = d2
                """
            elif (s == len(all_shifts) - 1):
                s = 0
                d += 1
            else:
                s += 1
            """
            for d in all_days:
                for s in all_shifts:
                    shifts_worked.append(shifts[(n, d, s)])
            """

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