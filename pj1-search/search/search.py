# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]


class node:
    """define node"""

    def __init__(self, state, parent, path_cost, action,):
        self.state = state
        self.parent = parent
        self.path_cost = path_cost
        self.action = action


def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"

    '''class node is defined before this function '''
    explored = []
    path = []
    fringe = util.Stack()
    node_test = node(problem.getStartState(), None, 0, '')
    fringe.push(node_test)
    while not fringe.isEmpty():
        # Get the current node
        node_cur = fringe.pop()
        # current state is the goal, return the path
        if problem.isGoalState(node_cur.state):
            while node_cur.parent:
                path.append(node_cur.action)
                node_cur = node_cur.parent
            path.reverse()
            return path
        # current state has been visited, ignore it and continue
        if node_cur.state in explored:
            continue
        explored.append(node_cur.state)
        successors = problem.getSuccessors(node_cur.state)
        # Iterate over the children of this node
        for item in successors:
            # successor nodes that have been visited are not pushed to the stack
            if item[0] in explored:
                continue
            node_successor = node(state=item[0], parent=node_cur, path_cost = node_cur.path_cost, action=item[1])
            # path_cost can be ignored in dfs because the algorithm doesn't use it
            # update fringe
            fringe.push(node_successor)
    return "No path!"
    util.raiseNotDefined()


def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    explored = []
    path = []
    fringe = util.Queue()
    node_test = node(problem.getStartState(), None, 0, '')
    fringe.push(node_test)
    while not fringe.isEmpty():
        # Get the current node
        node_cur = fringe.pop()
        # current state has been visited, ignore it and continue
        if node_cur.state in explored:
            continue
        explored.append(node_cur.state)
        successors = problem.getSuccessors(node_cur.state)
        # Iterate over the children of this node
        for item in successors:
            node_suc = node(item[0], node_cur, node_cur.path_cost, item[1])
            # path_cost can be ignored in bfs because the algorithm doesn't use it
            if problem.isGoalState(item[0]):
            # goal test has been moved here in keeping with the slide
                node_goal = node_suc
                while node_goal.parent:
                    path.append(node_goal.action)
                    node_goal = node_goal.parent
                path.reverse()
                return path
            # update fringe if the successor node has not been accessed
            if item[0] not in explored:
                fringe.push(node_suc)

    return "No path!"
    util.raiseNotDefined()


def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    node_test = node(problem.getStartState(), None, 0, None)
    path = []
    explored = []
    fringe = util.PriorityQueue()
    fringe.update(node_test, node_test.path_cost)
    while not fringe.isEmpty():
        # Get the current node
        node_cur = fringe.pop()
        # current state is the goal, return the path
        if problem.isGoalState(node_cur.state):
            while node_cur.parent:
                path.append(node_cur.action)
                node_cur = node_cur.parent
            path.reverse()
            return path
        # current state has been visited, ignore it and continue
        if node_cur.state in explored:
            continue
        explored.append(node_cur.state)
        successors = problem.getSuccessors(node_cur.state)
        # Iterate over the children of this node
        for item in successors:
            node_suc = node(item[0], node_cur, node_cur.path_cost + item[2], item[1])
            if node_suc.state not in explored:
                fringe.update(item= node_suc, priority= node_suc.path_cost)


    util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"

    class Node:
        # define Node
        # node for aStarSearch, added an attribute, heuristic_cost
        def __init__(self, state, parent, path_cost, heuristic_cost, action, ):
            self.state = state
            self.parent = parent
            self.path_cost = path_cost
            self.heuristic_cost = heuristic_cost
            self.action = action

    node_test = Node(problem.getStartState(), None, 0, heuristic(problem.getStartState(), problem), None)
    # priority = node_test.path_cost + node_test.heuristic_cost = g(n) + h(n)
    path = []
    explored = []
    fringe = util.PriorityQueue()
    fringe.update(node_test, node_test.path_cost + node_test.heuristic_cost)
    while not fringe.isEmpty():
        node_cur = fringe.pop()
        if problem.isGoalState(node_cur.state):
            while node_cur.parent:
                path.append(node_cur.action)
                node_cur = node_cur.parent
            path.reverse()
            return path
        if node_cur.state in explored:
            continue
        explored.append(node_cur.state)
        successors = problem.getSuccessors(node_cur.state)
        for item in successors:
            node_suc = Node(item[0], node_cur, node_cur.path_cost + item[2], heuristic(item[0], problem), item[1])
            if node_suc.state not in explored:
                fringe.update(item=node_suc, priority=node_suc.path_cost + node_suc.heuristic_cost)

    util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
