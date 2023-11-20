import time
import random
import heapq
from collections import namedtuple, deque

algorithm = namedtuple('Algorithm', ['name', 'func'])


class Board:
    @staticmethod
    def translate_to_2D(index):
        """Returns a tuple of 2D coordinate equivalent"""
        return index // 3, index % 3

    @staticmethod
    def manhattan_distance(x1, y1, x2, y2):
        """Returns a Manhattan distance between two points"""
        return abs(x1 - x2) + abs(y1 - y2)

    @staticmethod
    def valid_actions(state):
        """Generates valid actions for a given state"""
        blank_index = state.index(0)
        if blank_index > 2:
            yield 'U'
        if blank_index < 6:
            yield 'D'
        if blank_index % 3 > 0:
            yield 'L'
        if blank_index % 3 < 2:
            yield 'R'

    @staticmethod
    def transform(state, action):
        """Returns a new instance of a state when an action is applied"""
        state = [*state]
        blank_index = state.index(0)
        if action == 'U':
            state[blank_index], state[blank_index -
                                      3] = state[blank_index - 3], state[blank_index]
        elif action == 'D':
            state[blank_index], state[blank_index +
                                      3] = state[blank_index + 3], state[blank_index]
        elif action == 'L':
            state[blank_index], state[blank_index -
                                      1] = state[blank_index - 1], state[blank_index]
        elif action == 'R':
            state[blank_index], state[blank_index +
                                      1] = state[blank_index + 1], state[blank_index]
        return tuple(state)

    @staticmethod
    def inversions(state):
        """Returns the inversion sum of a state"""
        inversion_sum = 0
        for i in range(9):
            for j in range(i + 1, 9):
                if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                    inversion_sum += 1
        return inversion_sum

    @staticmethod
    def is_solvable(state):
        """Checks if a state is solvable or not"""
        return Board.inversions(state) % 2 == 0

    @staticmethod
    def create_solvable_state():
        """Returns a random solvable state"""
        state = [*range(9)]
        while True:
            random.shuffle(state)
            if Board.is_solvable(state):
                return tuple(state)

    @staticmethod
    def solve(state, func):
        """Returns the solution of a state given a search algorithm"""
        board_node = BoardNode(state)

        start_time = time.time()
        final_node, nodes_expanded, max_search_depth = func(board_node)
        final_time = time.time()

        path_to_goal = final_node.actions()
        time_elapsed = final_time - start_time

        return path_to_goal, nodes_expanded, max_search_depth, time_elapsed

    @staticmethod
    def draw(state):
        """Returns a string representation of a state"""
        return '{} {} {}\n{} {} {}\n{} {} {}'.format(*state)


class Node:
    def __init__(self, parent=None, depth=0):
        self.parent = parent
        self.depth = depth
        self.nodes = []

    def add_node(self, node):
        """Adds a new node to the children of the current node"""
        self.nodes.append(node)

    def iterate_ancestors(self):
        """Generates the ancestor nodes of the current node"""
        curr_node = self
        while curr_node:
            yield curr_node
            curr_node = curr_node.parent


class BoardNode(Node):
    def __init__(self, state, action=None, parent=None, depth=0):
        super().__init__(parent, depth)
        self.state = state
        self.action = action
        self.goal = tuple(range(9))
        self.heuristic_func = Board.manhattan_distance
        self.nodes_expanded = 0

    def cost(self):
        """Returns the heuristic cost of the state"""
        heuristic_sum = 0
        for index, item in enumerate(self.state):
            curr_x, curr_y = Board.translate_to_2D(index)
            goal_x, goal_y = Board.translate_to_2D(self.goal.index(item))
            heuristic_sum += self.heuristic_func(curr_x,
                                                 curr_y, goal_x, goal_y)
        return heuristic_sum + self.depth

    def expand(self):
        """Expands valid actions as the children of the current state"""
        if not self.nodes:
            for action in Board.valid_actions(self.state):
                self.add_node(BoardNode(
                    Board.transform(self.state, action),
                    parent=self,
                    action=action,
                    depth=self.depth + 1
                ))

    def actions(self):
        """Returns all the actions of the ancestor states"""
        return tuple(node.action for node in self.iterate_ancestors())[-2::-1]

    def is_goal(self):
        """Checks if the current state is equal to the goal state"""
        return self.state == self.goal

    def __lt__(self, other):
        """Checks if the cost of the current state is less than the cost of the other state"""
        return self.cost() < other.cost()

    def __eq__(self, other):
        """Checks if the cost of the current state is equal to the cost of the other state"""
        return self.cost() == other.cost()

    def __str__(self):
        """Returns the string representation of the state"""
        return Board.draw(self.state)

    def __repr__(self):
        """Returns the actual representation of the state"""
        return f'Board(state={self.state}, action={self.action}, depth={self.depth})'


def A_STAR(start_node):
    """Returns the goal node"""
    frontier = []
    explored_nodes = set()
    nodes_expanded = 0
    max_search_depth = 0

    heapq.heappush(frontier, start_node)

    while frontier:
        node = heapq.heappop(frontier)
        explored_nodes.add(node.state)

        if node.is_goal():
            return node, nodes_expanded, max_search_depth

        node.expand()
        nodes_expanded += 1

        for neighbor in node.nodes:
            if neighbor.state not in explored_nodes:
                heapq.heappush(frontier, neighbor)
                explored_nodes.add(neighbor.state)

                if neighbor.depth > max_search_depth:
                    max_search_depth = neighbor.depth

    return None


def BFS(start_node):
    """Returns the goal node"""
    frontier = deque()
    explored_nodes = set()
    nodes_expanded = 0
    max_search_depth = 0

    frontier.append(start_node)

    while frontier:
        node = frontier.popleft()
        explored_nodes.add(node.state)

        if node.is_goal():
            return node, nodes_expanded, max_search_depth

        node.expand()
        nodes_expanded += 1

        for neighbor in node.nodes:
            if neighbor.state not in explored_nodes:
                frontier.append(neighbor)
                explored_nodes.add(neighbor.state)

                if neighbor.depth > max_search_depth:
                    max_search_depth = neighbor.depth

    return None


def DFS(start_node):
    max_depth = 1
    while True:
        result = limited_DFS(start_node, max_depth)
        if result is not None:
            return result
        max_depth += 1


def limited_DFS(start_node, max_depth):
    frontier = deque()
    explored_nodes = set()
    nodes_expanded = 0

    frontier.append((start_node, 0))

    while frontier:
        node, depth = frontier.pop()
        explored_nodes.add(node.state)

        if node.is_goal():
            return node, nodes_expanded, depth

        if depth < max_depth:
            node.expand()
            nodes_expanded += 1
            for neighbor in reversed(node.nodes):
                if neighbor.state not in explored_nodes:
                    frontier.append((neighbor, depth + 1))

    return None


def UCS(start_node):
    frontier = []
    heapq.heappush(frontier, start_node)
    explored = set()

    while frontier:
        current_node = heapq.heappop(frontier)
        explored.add(current_node.state)

        if current_node.is_goal():
            return current_node, len(explored), current_node.depth

        current_node.expand()
        for child in current_node.nodes:
            if child.state not in explored:
                heapq.heappush(frontier, child)

    return None, 0, 0


def Greedy(node):
    """Greedy search algorithm"""
    frontier = []
    heapq.heappush(frontier, node)
    explored = set()

    while frontier:
        current_node = heapq.heappop(frontier)
        explored.add(current_node.state)

        if current_node.is_goal():
            return current_node, len(explored), current_node.depth

        current_node.expand()
        current_node.nodes.sort(key=lambda x: x.heuristic_func(
            *Board.translate_to_2D(x.state.index(0)), *Board.translate_to_2D(x.goal.index(0))))

        for child in current_node.nodes:
            if child.state not in explored:
                heapq.heappush(frontier, child)

    return None, 0, 0


def BEAM_SEARCH(start_node, beam_width=3):
    """Returns the goal node"""
    frontier = []
    explored_nodes = set()
    nodes_expanded = 0
    max_search_depth = 0

    heapq.heappush(frontier, (start_node.cost(), start_node))

    while frontier:
        node = heapq.heappop(frontier)[1]
        explored_nodes.add(node.state)

        if node.is_goal():
            return node, nodes_expanded, max_search_depth

        node.expand()
        nodes_expanded += 1

        successors = []
        for child in node.nodes:
            if child.state not in explored_nodes:
                successors.append(child)

        successors.sort()

        for i in range(min(beam_width, len(successors))):
            child = successors[i]
            heapq.heappush(frontier, (child.cost(), child))
            explored_nodes.add(child.state)

            if child.depth > max_search_depth:
                max_search_depth = child.depth

    return None

#Hill Climbing
def Hill_Climbing(start_node):
    """Hill Climbing search algorithm"""
    frontier = []
    heapq.heappush(frontier, start_node)
    explored = set()

    while frontier:
        current_node = heapq.heappop(frontier)
        explored.add(current_node.state)

        if current_node.is_goal():
            return current_node, len(explored), current_node.depth

        current_node.expand()
        for child in current_node.nodes:
            if child.state not in explored:
                heapq.heappush(frontier, child)

    return None, 0, 0


if __name__ == '__main__':
    # start state
    start_state = Board.create_solvable_state()
    print('Start state:')
    print(Board.draw(start_state))

    # Solved using A*
    print('\nFinding...')
    final_node, nodes_expanded, max_search_depth, time_elapsed = Board.solve(
        start_state, A_STAR)

    if final_node is not None:
        if isinstance(final_node, BoardNode):
            path_to_goal = final_node.actions()
            print(
                f'Done in {round(time_elapsed, 4)} second(s) with {len(path_to_goal)} moves using A*')
            print(
                f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
            print('Actions:', *path_to_goal)
        else:
            print("No solution found.")
    else:
        print("No solution found.")

 # Solved using DFS with heuristic (Manhattan distance)
    result = DFS(start_state)
    if result is not None:
        final_node, nodes_expanded, max_search_depth = result
        path_to_goal = final_node.actions()
        print(
            f'Done with {len(path_to_goal)} moves using DFS')
        print(
            f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
        print('Actions:', *path_to_goal)
    else:
        print("No solution found.")

# Solved using BFS
    print('\nFinding...')
    path_to_goal, nodes_expanded, max_search_depth, time_elapsed = Board.solve(
        start_state, BFS)

    if final_node is not None:
        path_to_goal = final_node.actions()
        print(
            f'Done in {round(time_elapsed, 4)} second(s) with {len(path_to_goal)} moves using BFS')
        print(
            f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
        print('Actions:', *path_to_goal)
    else:
        print("No solution found.")

 # Solved using UCS
    print('\nFinding solution...')
    final_node, nodes_expanded, max_search_depth, time_elapsed = Board.solve(
        start_state, UCS)

    if final_node is not None:
        if isinstance(final_node, BoardNode):
            path_to_goal = final_node.actions()
            print(
                f'Done in {round(time_elapsed, 4)} second(s) with {len(path_to_goal)} moves using UCS')
            print(
                f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
            print('Actions:', *path_to_goal)
        else:
            print("No solution found.")
    else:
        print("No solution found.")

    # Solved using Greedy
    print('\nFinding...')
    final_node, nodes_expanded, max_search_depth, time_elapsed = Board.solve(
        start_state, Greedy)

    if final_node is not None:
        if isinstance(final_node, BoardNode):
            path_to_goal = final_node.actions()
            print(
                f'Done in {round(time_elapsed, 4)} second(s) with {len(path_to_goal)} moves using Greedy')
            print(
                f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
            print('Actions:', *path_to_goal)
        else:
            print("No solution found.")
    else:
        print("No solution found.")

# solved using Beam Search
    print('\nFinding solution...')
    path_to_goal, nodes_expanded, max_search_depth, time_elapsed = Board.solve(
        start_state, BEAM_SEARCH)

    print(
        f'Done in {round(time_elapsed, 4)}s with {len(path_to_goal)} moves using Beam Search (beam_width=3)')
    print(f'Nodes expanded: {nodes_expanded}')
    print(f'Max search depth: {max_search_depth}')
    print('Actions:', *path_to_goal)
#solve using Hill Climbing
    print('\nFinding solution...')
    path_to_goal, nodes_expanded, max_search_depth, time_elapsed = Board.solve(
        start_state, Hill_Climbing)

    print(
        f'Done in {round(time_elapsed, 4)}s with {len(path_to_goal)} moves using Hill Climbing')
    print(f'Nodes expanded: {nodes_expanded}')
    print(f'Max search depth: {max_search_depth}')
    print('Actions:', *path_to_goal)
    