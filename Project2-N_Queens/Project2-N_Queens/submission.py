import copy
from csp import CSP


def create_n_queens_csp(n=8):
    """Create an N-Queen problem on the board of size n * n.

    You should call csp.add_variable() and csp.add_binary_factor().

    Args:
        n: int, number of queens, or the size of one dimension of the board.

    Returns
        csp: A CSP problem with correctly configured factor tables
        such that it can be solved by a weighted CSP solver
    """
    csp = CSP()
    # TODO: Problem b
    # TODO: BEGIN_YOUR_CODE
    # The domain of each variable is Width
    Width = list(range(1,n+1))
    # Create variables, the variable i represents the Queen of the i-th row
    # There is no unary factor
    for i in range(n):
        csp.add_variable(i+1, Width)
    # Add binary constraints
    for i in range(1, n+1):
        for j in range(1, n+1):
            if i == j:
                continue
            # Two queens cannot be in the same column or diagonal
            csp.add_binary_factor(i, j, lambda x, y: x!=y and abs(x-y)!=abs(i-j))


    #raise NotImplementedError
    # TODO: END_YOUR_CODE
    return csp


class BacktrackingSearch:
    """A backtracking algorithm that solves CSP.

    Attributes:
        num_assignments: keep track of the number of assignments
            (identical when the CSP is unweighted)
        num_operations: keep track of number of times backtrack() gets called
        first_assignment_num_operations: keep track of number of operations to
            get to the very first successful assignment (maybe not optimal)
        all_assignments: list of all solutions found

        csp: a weighted CSP to be solved
        mcv: bool, if True, use Most Constrained Variable heuristics
        ac3: bool, if True, AC-3 will be used after each variable is made
        domains: dictionary of domains of every variable in the CSP

    Usage:
        search = BacktrackingSearch()
        search.solve(csp)
    """

    def __init__(self):
        self.num_assignments = 0
        self.num_operations = 0
        self.first_assignment_num_operations = 0
        self.all_assignments = []

        self.csp = None
        self.mcv = False
        self.ac3 = False
        self.domains = {}

    def reset_results(self):
        """Resets the statistics of the different aspects of the CSP solver."""
        self.num_assignments = 0
        self.num_operations = 0
        self.first_assignment_num_operations = 0
        self.all_assignments = []

    def check_factors(self, assignment, var, val):
        """Check consistency between current assignment and a new variable.

        Given a CSP, a partial assignment, and a proposed new value for a
        variable, return the change of weights after assigning the variable
        with the proposed value.

        Args:
            assignment: A dictionary of current assignment.
                Unassigned variables do not have entries, while an assigned
                variable has the assigned value as value in dictionary.
                e.g. if the domain of the variable A is [5,6],
                and 6 was assigned to it, then assignment[A] == 6.
            var: name of an unassigned variable.
            val: the proposed value.

        Returns:
            bool
                True if the new variable with value can satisfy constraint,
                otherwise, False
        """
        assert var not in assignment
        if self.csp.unary_factors[var]:
            if self.csp.unary_factors[var][val] == 0:
                return False
        for var2, factor in self.csp.binary_factors[var].items():
            if var2 not in assignment:
                continue
            if factor[val][assignment[var2]] == 0:
                return False
        return True

    def solve(self, csp, mcv=False, ac3=False):
        """Solves the given unweighted CSP using heuristics.

        Note that we want this function to find all possible assignments.
        The results are stored in the variables described in
            reset_result().

        Args:
            csp: A unweighted CSP.
            mcv: bool, if True, Most Constrained Variable heuristics is used.
            ac3: bool, if True, AC-3 will be used after each assignment of an
            variable is made.
        """
        self.csp = csp
        self.mcv = mcv
        self.ac3 = ac3
        self.reset_results()
        self.domains = {var: list(self.csp.values[var])
                        for var in self.csp.variables}
        self.backtrack({})

    def backtrack(self, assignment):
        """Back-tracking algorithms to find all possible solutions to the CSP.

        Args:
            assignment: a dictionary of current assignment.
                Unassigned variables do not have entries, while an assigned
                variable has the assigned value as value in dictionary.
                    e.g. if the domain of the variable A is [5, 6],
                    and 6 was assigned to it, then assignment[A] == 6.
        """
        self.num_operations += 1

        num_assigned = len(assignment.keys())
        if num_assigned == self.csp.vars_num:
            self.num_assignments += 1
            new_assignment = {}
            for var in self.csp.variables:
                new_assignment[var] = assignment[var]
            self.all_assignments.append(new_assignment)
            if self.first_assignment_num_operations == 0:
                self.first_assignment_num_operations = self.num_operations
            return

        var = self.get_unassigned_variable(assignment)
        ordered_values = self.domains[var]

        if not self.ac3:
            # TODO: Problem a
            # TODO: BEGIN_YOUR_CODE
            for value in ordered_values:
                # Check whether the current value violates the constraint
                if self.check_factors(assignment, var, value):
                    assignment[var] = value
                    self.backtrack(assignment)
                    del assignment[var]

            #raise NotImplementedError
            # TODO: END_YOUR_CODE

        else:
            # TODO: Problem d
            # TODO: BEGIN_YOUR_CODE

            for value in ordered_values:
                if self.check_factors(assignment, var, value):
                    assignment[var] = value
                    # The following operations will change the domains. domain_cur saves the current domains
                    domain_cur = copy.deepcopy(self.domains)
                    # After assignment, the domain has only the value just assigned
                    self.domains[var] = [value]
                    if self.arc_consistency_check(var):
                        self.backtrack(assignment)
                    # If this solution is ultimately unsuccessful, the domains must be restored when backtracking
                    self.domains = copy.deepcopy(domain_cur)
                    del assignment[var]

            #raise NotImplementedError
            # TODO: END_YOUR_CODE


    def get_unassigned_variable(self, assignment):
        """Get a currently unassigned variable for a partial assignment.

        If mcv is True, Use heuristic: most constrained variable (MCV)
        Otherwise, select a variable without any heuristics.

        Most Constrained Variable (MCV):
            Select a variable with the least number of remaining domain values.
            Hint: self.domains[var] gives you all the possible values
            Hint: choose the variable with lowest index in self.csp.variables
                for ties


        Args:
            assignment: a dictionary of current assignment.

        Returns
            var: a currently unassigned variable.
        """
        if not self.mcv:
            for var in self.csp.variables:
                if var not in assignment:
                    return var
        else:
            # TODO: Problem c

            # TODO: BEGIN_YOUR_CODE

            # var_mcv: variable with the least number of remaining domain values
            # num_ava: the number of available values in the domain of var_mcv
            var_mcv = self.csp.variables[0]
            num_ava = max([len(self.domains[var]) for var in self.csp.variables]) + 1
            for var in self.csp.variables:
                # Search for unassigned  variables
                if var in assignment:
                    continue
                num_cur = 0
                for value in self.domains[var]:
                    if self.check_factors(assignment, var, value):  # The value is available
                        num_cur += 1
                if num_cur < num_ava:
                    num_ava = num_cur
                    var_mcv = var
            return var_mcv

            #raise NotImplementedError
            # TODO: END_YOUR_CODE

    def arc_consistency_check(self, var):
        """AC-3 algorithm.

        The goal is to reduce the size of the domain values for the unassigned
        variables based on arc consistency.

        Hint: get variables neighboring variable var:
            self.csp.get_neighbor_vars(var)

        Hint: check if a value or two values are inconsistent:
            For unary factors
                self.csp.unaryFactors[var1][val1] == 0
            For binary factors
                self.csp.binaryFactors[var1][var2][val1][val2] == 0

        Args:
            var: the variable whose value has just been set

        Returns
            boolean: succeed or not
        """
        # TODO: Problem d
        # TODO: BEGIN_YOUR_CODE

        arc_queue = []
        # Check all the arcs in the graph, nodes already assigned have no effect
        # (x,y) represents arc x->y
        for x in self.csp.variables:
            for y in self.csp.variables:
                if x == y:
                    continue
                arc_queue.append((x, y))

        while len(arc_queue) != 0 :
            # var_x is tail, and var_y is head
            # Deleting from the head or tail of the queue does not affect the result here
            var_x, var_y = arc_queue.pop(0)
            removed = False
            # Check arc consistency x->y
            # list[:] will extract all elements first, and can avoid omissions due to list changes in the loop
            for value_x in self.domains[var_x][:]:
                # num_uncon : the number of y that break arc consistency
                num_uncon = 0
                for value_y in self.domains[var_y]:
                    if not self.csp.binary_factors[var_x][var_y][value_x][value_y]:
                        num_uncon += 1
                # If all y in domains[var_y] breaks arc consistency.
                if num_uncon == len(self.domains[var_y]):
                    self.domains[var_x].remove(value_x)
                    # x loses a value, neighbors of x needs to be rechecked.
                    removed = True
                    # If the domian is empty, return False and backtracking
                    if len(self.domains[var_x]) == 0:
                        return False

            if removed:
                # Recheck neighbors of x
                neighbors = self.csp.get_neighbor_vars(var_x)
                for var_neighbor in neighbors:
                    new_arc = (var_neighbor, var_x)
                    arc_queue.append(new_arc)

        return True

        #raise NotImplementedError
        # TODO: END_YOUR_CODE
