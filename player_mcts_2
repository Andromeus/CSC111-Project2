"""CSC111 Project 2 ALIGNQUATTRO

MCTS SEARCH FILE

This file contains the MCTS search logic for the AlignQuattro AI player. This includes:
    - An MCTSPlayer class, which uses MCTS over a DAG to select moves
    - Helper methods for selection, expansion, simulation, backpropagation, and move choice
"""

from __future__ import annotations

import math
import random
import copy
from typing import Any
from dataclasses import dataclass, field

import game_logic
from game_logic import Player, AlignQuattroGame
from mcts_dag import DAGNode, zobrist_hash, get_or_create_node


################################################################################
# Tree Node (used when is_dag=False)
################################################################################

@dataclass
class _TreeNode:
    """A node in a tree-based MCTS search."""
    visit_count: int = 0
    value_sum: float = 0.0
    children: dict[int, "_TreeNode"] = field(default_factory=dict)


################################################################################
# MCTS Player
################################################################################

class MCTSPlayer(Player):
    """An AlignQuattro player that chooses moves using Monte Carlo Tree (or Graph) Search.

    Instance Attributes:
        - num_searches: the number of MCTS iterations to run before choosing a move
        - exploration_weight: the exploration constant c used in the UCB formula
        - is_dag: whether to run a DAG MCTS search or a regular tree implementation
        - _root: the current root node for the preserved DAG, if any
        - _transposition_table: maps Zobrist hashes to DAGNodes (used when is_dag=True)

    Representation Invariants:
        - self.num_searches >= 1
        - self.exploration_weight > 0
    """
    num_searches: int
    exploration_weight: float
    is_dag: bool
    _root: Any | None
    _transposition_table: dict[int, DAGNode]

    def __init__(self, num_searches: int = 400,
                 exploration_weight: float = math.sqrt(2),  # FIX 1: was sqrt(2), missing math.
                 is_dag: bool = True) -> None:
        """Initializes the MCTS player.

        Preconditions:
            - num_searches >= 1
            - exploration_weight > 0

        >>> player = MCTSPlayer(50, 1.5)
        >>> player.num_searches
        50
        >>> player.exploration_weight
        1.5
        """
        self.num_searches = num_searches
        self.exploration_weight = exploration_weight
        self.is_dag = is_dag
        self._root = None
        self._transposition_table = {}

    def make_move(self, game: AlignQuattroGame) -> int:
        """Return the move chosen by MCTS for the given game state.

        Preconditions:
            - game.get_outcome() == 'in progress'
            - len(game.get_available_columns()) > 0

        >>> game = AlignQuattroGame()
        >>> player = MCTSPlayer(1)
        >>> move = player.make_move(game)
        >>> move in range(7)
        True
        """
        return self._mcts_search(game)

    def _mcts_search(self, root_game: AlignQuattroGame) -> int:
        """Run MCTS from root_game and return the chosen column.

        Preconditions:
            - root_game.get_outcome() == 'in progress'
            - len(root_game.get_available_columns()) > 0
        """
        copy_of_root = copy.deepcopy(root_game)
        if self.is_dag:
            root_node = self._retrieve_or_create_dag_node(copy_of_root)
        else:
            root_node = _TreeNode()

        self._root = root_node
        for _ in range(self.num_searches):
            self._run_one_iteration(root_node, root_game)

        return self._choose_final_move(root_node)

    def _run_one_iteration(self, root_node: Any, root_game: AlignQuattroGame) -> None:
        """Run one complete MCTS iteration: selection → expansion → simulation → backpropagation.

        Preconditions:
            - root_game.get_outcome() == 'in progress'
        """
        iter_game = copy.deepcopy(root_game)
        path = self._select(root_node, iter_game)
        leaf = path[-1]

        if iter_game.get_outcome() == "in progress":
            expanded_child = self._expand(leaf, iter_game)
            path.append(expanded_child)

        root_is_red = self._root_player_is_red(root_game)
        reward = self._simulate(iter_game, root_is_red)
        self._backpropagate(path, reward)

    def _select(self, root_node: Any, game: AlignQuattroGame) -> list[Any]:
        """Traverse the DAG/tree from root_node to a leaf and return the visited path.

        Stops when the game is terminal or when the current node has at least one
        unexpanded legal move (so _expand can add it next).

        The same moves applied to reach each node are applied to game so it stays
        synchronised with the leaf at the end of the path.

        Preconditions:
            - game.get_outcome() in {'in progress', 'red win', 'yellow win', 'tie'}
        """
        current_node = root_node
        path = [current_node]

        while game.get_outcome() == "in progress":
            legal_moves = game.get_available_columns()

            # Stop if there is any unexpanded child — _expand will handle it
            if len(current_node.children) != len(legal_moves):
                break

            # All children exist: descend to the best one by UCB
            move, next_node = self._find_best_child(current_node)
            game.make_move(move)
            current_node = next_node
            path.append(current_node)

        return path

    def _expand(self, node: Any, game: AlignQuattroGame) -> Any:
        """Expand node by adding one previously unexplored legal move.

        Picks a random unexpanded move, applies it to game, obtains or creates
        the child node (via DAG lookup or fresh _TreeNode), stores it in
        node.children, and returns it.

        Preconditions:
            - game.get_outcome() == 'in progress'
        """
        legal_moves = game.get_available_columns()
        unexpanded = [m for m in legal_moves if m not in node.children]

        # Pick a random unexplored move
        move = random.choice(unexpanded)
        game.make_move(move)

        # Obtain child — reuse existing DAG node or create a fresh tree node
        if self.is_dag:
            child = self._retrieve_or_create_dag_node(game)
        else:
            child = _TreeNode()

        node.children[move] = child
        return child

    def _simulate(self, game: AlignQuattroGame, root_is_red: bool) -> float:
        """Play a random rollout from game to a terminal state and return the reward.

        Reward is from the root player's perspective:
            +1.0 → root player wins
             0.0 → draw
            -1.0 → root player loses

        Preconditions:
            - game.get_outcome() in {'in progress', 'red win', 'yellow win', 'tie'}
        """
        sim_game = copy.deepcopy(game)
        while sim_game.get_outcome() == "in progress":
            move = random.choice(sim_game.get_available_columns())
            sim_game.make_move(move)
        return self._reward_from_outcome(sim_game.get_outcome(), root_is_red)

    def _backpropagate(self, path: list[Any], reward: float) -> None:
        """Update visit counts and value sums along the visited path.

        Because players alternate turns, the reward is negated at each step
        as we walk back up the path.

        DAG safety: uses id-based visited set so each node is updated at most
        once per iteration even if it appears via multiple paths.

        Preconditions:
            - all(node is not None for node in path)
            - reward in {-1.0, 0.0, 1.0}

        >>> player = MCTSPlayer()
        >>> player._backpropagate([], 0.0)
        """
        visited_ids: set[int] = set()
        for depth, node in enumerate(path):
            node_id = id(node)
            if node_id in visited_ids:
                continue
            visited_ids.add(node_id)

            node.visit_count += 1
            # Flip sign based on depth: root player's reward is positive at depth 0
            node.value_sum += reward if depth % 2 == 0 else -reward

    def _find_best_child(self, node: Any) -> tuple[int, Any]:
        """Return the (move, child) pair with the highest UCB score.

        Used during selection to greedily descend the tree.

        Preconditions:
            - len(node.children) > 0
        """
        best_move = max(node.children, key=lambda m: self._ucb_score(node, node.children[m]))
        return best_move, node.children[best_move]

    def _ucb_score(self, parent: Any, child: Any) -> float:
        """Return the UCB1 score for child relative to parent.

        The exploitation term is NEGATED because backpropagation stores values
        from alternating perspectives (root at depth 0, opponent at depth 1...).
        A child node's value_sum is from the child's player's perspective, which
        is the OPPOSITE of what the parent wants to maximise. Negating converts
        it back to the parent's perspective so selection always picks the best
        move for the player currently choosing.

        Unvisited children score infinity so they are always tried first.

        Preconditions:
            - parent is not None
            - child is not None
        """
        if child.visit_count == 0:
            return float('inf')
        exploitation = -(child.value_sum / child.visit_count)  # negate: parent's perspective
        exploration = self.exploration_weight * math.sqrt(
            math.log(parent.visit_count) / child.visit_count
        )
        return exploitation + exploration

    def _choose_final_move(self, root_node: Any) -> int:
        """Return the move with the highest visit count from root_node.

        Visit count is more robust than raw Q-value because a move accumulates
        high visits only if it consistently looked good across many simulations.

        Preconditions:
            - len(root_node.children) > 0
        """
        return max(root_node.children, key=lambda m: root_node.children[m].visit_count)

    def _promote_child_to_root(self, current_root: Any, move: int) -> None:
        """Update the stored root to the child reached by move, preserving past statistics.

        Preconditions:
            - 0 <= move <= 6
        """
        if current_root is not None and move in current_root.children:
            self._root = current_root.children[move]
        else:
            self._root = None

    def _reward_from_outcome(self, outcome: str, root_is_red: bool) -> float:
        """Convert a terminal game outcome into a rollout reward.

        Preconditions:
            - outcome in {'red win', 'yellow win', 'tie'}

        >>> player = MCTSPlayer()
        >>> player._reward_from_outcome('tie', True)
        0.0
        >>> player._reward_from_outcome('red win', True)
        1.0
        >>> player._reward_from_outcome('yellow win', True)
        -1.0
        >>> player._reward_from_outcome('red win', False)
        -1.0
        """
        if outcome == 'tie':
            return 0.0
        elif outcome == 'red win':
            return 1.0 if root_is_red else -1.0
        else:
            return -1.0 if root_is_red else 1.0

    def _root_player_is_red(self, game: AlignQuattroGame) -> bool:
        """Return whether the player to move at game is red.

        Preconditions:
            - game.get_outcome() == 'in progress'
        """
        # FIX 4: game.is_red_turn() now exists — added as a public getter in game_logic.py
        return game.is_red_turn()

    def _retrieve_or_create_dag_node(self, root_copy: AlignQuattroGame) -> DAGNode:
        # FIX 2+3: return type annotation was on its own line (SyntaxError),
        # and 'DagNode' was wrong capitalisation — fixed to DAGNode
        """Return the DAG node for this game state, creating it if it does not exist.

        Preconditions:
            - self.is_dag

        >>> player = MCTSPlayer(is_dag=True)
        >>> game = AlignQuattroGame()
        >>> node1 = player._retrieve_or_create_dag_node(game)
        >>> node2 = player._retrieve_or_create_dag_node(game)
        >>> node1 is node2
        True
        """
        state_hash = zobrist_hash(root_copy)
        return get_or_create_node(state_hash, self._transposition_table)
