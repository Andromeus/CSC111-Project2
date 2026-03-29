"""CSC111 Project 2 ALIGNQUATTRO

DAG FILE

This file contains the DAG (Directed Acyclic Graph) logic for the MCTS player. This includes:
    - A _DAGNode class, representing a single node in the DAG, which stores visit count, value sum, and children
    - A _zobrist_hash function, which hashes a board state to a unique 64-bit integer
    - A _get_or_create_node function, which looks up or creates a node in the transposition table
"""

from __future__ import annotations

import random
import math
import game_logic_2


################################################################################
# Zobrist Hashing
################################################################################

# Map each piece type to an index for the Zobrist table
_PIECE_INDEX = {'empty': 0, 'red': 1, 'yellow': 2}

# Pre-generate a random 64-bit integer for every (row, col, piece_type) triple.
# The hash of a board is the XOR of all matching entries.
_ZOBRIST_TABLE: list[list[list[int]]] = [
    [
        [random.getrandbits(64) for _ in range(3)]   # one entry per piece type
        for _ in range(7)                             # 7 columns
    ]
    for _ in range(6)                                 # 6 rows
]


def zobrist_hash(game: game_logic.AlignQuattroGame) -> int:
    """Return a 64-bit integer uniquely identifying the board state of the given game.

    Uses Zobrist hashing: each (row, col, piece_type) triple has a pre-assigned
    random number. The board hash is the XOR of all matching triples.

    Two boards that are identical in piece layout will always produce the same hash,
    regardless of the move order that produced them.

    >>> game = game_logic.AlignQuattroGame()
    >>> h1 = zobrist_hash(game)
    >>> game2 = game_logic.AlignQuattroGame()
    >>> h2 = zobrist_hash(game2)
    >>> h1 == h2  # same empty board → same hash
    True
    """
    board = game.get_board()
    h = 0
    for r in range(6):
        for c in range(7):
            piece_type = board[r][c].get_piece_type()
            piece_idx = _PIECE_INDEX[piece_type]
            h ^= _ZOBRIST_TABLE[r][c][piece_idx]
    return h


################################################################################
# DAG Node
################################################################################

class DAGNode:
    """A node in the MCTS DAG, representing a unique board position.

    Each node stores the statistics accumulated across all simulations that
    have passed through it, regardless of the path taken to reach it.

    Instance Attributes:
        - visit_count : total number of simulations that have passed through this node
        - value_sum   : cumulative result of those simulations (root player's POV)
        - children    : mapping from column index (0-6) to the child DAGNode reached
                        by playing that column

    Representation Invariants:
        - self.visit_count >= 0
        - all(0 <= col <= 6 for col in self.children)
    """
    visit_count: int
    value_sum: float
    children: dict[int, DAGNode]

    def __init__(self) -> None:
        """Initialize a DAGNode with no visits, no value, and no children."""
        self.visit_count = 0
        self.value_sum = 0.0
        self.children = {}

    def q_value(self) -> float:
        """Return the average simulation result through this node (exploitation term).

        Returns 0.0 for unvisited nodes to treat them as neutral before exploration.

        >>> node = DAGNode()
        >>> node.q_value()
        0.0
        >>> node.visit_count = 4
        >>> node.value_sum = 3.0
        >>> node.q_value()
        0.75
        """
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count

    def ucb_score(self, parent_visit_count: int, c: float = math.sqrt(2)) -> float:
        """Return the UCB1 score of this node given its parent's visit count.

        UCB1 balances:
            - Exploitation: prefer nodes with a high average value (q_value)
            - Exploration:  prefer nodes visited rarely relative to their parent

        Unvisited nodes return infinity so they are always selected before any
        visited node — every child must be tried at least once.

        The exploration constant c controls the tradeoff:
            - Higher c → more exploration
            - Lower  c → more exploitation
            - c = sqrt(2) is the standard theoretical default for win/loss/draw values

        Preconditions:
            - parent_visit_count >= 1

        >>> node = DAGNode()
        >>> node.ucb_score(10)  # unvisited → inf
        inf
        >>> node.visit_count = 5
        >>> node.value_sum = 3.0
        >>> score = node.ucb_score(10)
        >>> score > node.q_value()  # exploration bonus pushes score above raw Q
        True
        """
        if self.visit_count == 0:
            return float('inf')
        exploitation = self.q_value()
        exploration = c * math.sqrt(math.log(parent_visit_count) / self.visit_count)
        return exploitation + exploration


################################################################################
# Transposition Table
################################################################################

def get_or_create_node(
    board_hash: int,
    table: dict[int, DAGNode]
) -> DAGNode:
    """Return the DAGNode for the given board hash, creating it if it does not exist.

    This is the core of the DAG: if two different move sequences reach the same
    board state, they produce the same hash and therefore retrieve the same node.
    All simulations through that board position share one set of statistics.

    Mutates:
        - table: inserts a new DAGNode at board_hash if not already present

    >>> table = {}
    >>> node1 = get_or_create_node(12345, table)
    >>> node2 = get_or_create_node(12345, table)
    >>> node1 is node2  # same hash → same node object
    True
    >>> len(table)
    1
    >>> node3 = get_or_create_node(99999, table)
    >>> node3 is node1  # different hash → different node
    False
    >>> len(table)
    2
    """
    if board_hash not in table:
        table[board_hash] = DAGNode()
    return table[board_hash]
