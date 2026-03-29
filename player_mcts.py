"""Monte Carlo Tree Search player for Align Quattro."""
from __future__ import annotations
import math
import random
from typing import Any
import copy
from dataclasses import dataclass, field
from game_logic_2 import Player, AlignQuattroGame
from mcts_dag import DAGNode, zobrist_hash, get_or_create_node


@dataclass
class _TreeNode:
    """A node in a tree-based MCTS search."""
    visit_count: int = 0
    value_sum: float = 0.0
    children: dict[int, "_TreeNode"] = field(default_factory=dict)


class MCTSPlayer(Player):
    """An AlignQuattro player that chooses moves using Monte Carlo Tree (or Graph) Search.

    The player can either use a regular search tree for the MCTS, or a DAG-based approach search, which reuses nodes,
    depending on the value of self.is_dag.

    Instance Attributes:
        - num_searches: the number of MCTS iterations to run before choosing a move
        - exploration_weight: the exploration constant c used in the UCB formula
        - is_dag: whether to run a dag MCTS search or a regular tree implementation
        - transposition_table: maps hash keys to previously seen game states when using a DAG
        - _root: the current root node for the preserved DAG, if any

    Representation Invariants:
        - self.num_searches >= 1
        - self.exploration_weight > 0
    """
    num_searches: int
    exploration_weight: float
    is_dag: bool
    _transposition_table: dict
    _root: Any | None

    def __init__(self, num_searches: int = 400, exploration_weight: float = math.sqrt(2), is_dag: bool = True) -> None:
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
        self._transposition_table = {}
        self._root = None

    def make_move(self, game: AlignQuattroGame) -> int:
        """Return the move chosen by MCTS for the given game state.

        Preconditions:
            - game.get_outcome() == 'in progress'
            - len(game.get_available_columns()) > 0

        >>> game = AlignQuattroGame()
        >>> player = MCTSPlayer(1)
        >>> move = player.make_move(game)
        >>> 0 <= move <= 6
        True
        """
        return self._mcts_search(game)

    def _mcts_search(self, root_game: AlignQuattroGame) -> int:
        """Run MCTS from root_game and return the chosen move to make, based on the search results.

        It first obtains the root node, and then repeats the steps of MCTS: selection, expansion, simulation and
        backpropagation, and then it chooses the child move with the greatest visit count.

        Preconditions:
            - root_game.get_outcome() == 'in progress'
            - len(root_game.get_available_columns()) > 0

        >>> game = AlignQuattroGame()
        >>> player = MCTSPlayer()
        >>> isinstance(player._mcts_search(game), int)   # doctest: +SKIP
        True
        """
        # We do not want to mutate the original game state
        copy_of_root = copy.deepcopy(root_game)
        # Depending on the mode (DAG/Tree), we instantiate different objects
        if self.is_dag:
            root_node = self._retrieve_or_create_dag_node(copy_of_root)
        else:
            root_node = _TreeNode()

        self._root = root_node
        for _ in range(self.num_searches):
            self._run_one_iteration(root_node, root_game)

        return self._choose_final_move(root_node)

    def _run_one_iteration(self, root_node: Any, root_game: AlignQuattroGame) -> None:
        """Run one complete MCTS iteration on a deep copy of the original root_game starting at the given root:
        selection, expansion, simulation and backpropagation.

        Preconditions:
            - root_game.get_outcome() == 'in progress'

        >>> game = AlignQuattroGame()
        >>> player = MCTSPlayer()
        >>> player._run_one_iteration(None, game)   # doctest: +SKIP
        """
        iter_game = copy.deepcopy(root_game)
        path = self._select(root_node, iter_game)
        leaf = path[-1]  # Path is non-empty

        if iter_game.get_outcome() == "in progress":
            # Expansion step
            expanded_child = self._expand(leaf, iter_game)
            path.append(expanded_child)

        # Backpropagation step; note that the reward is different based on who the root player is (Red or Yellow)
        root_is_red = self._root_player_is_red(root_game)
        reward = self._simulate(iter_game, root_is_red)
        self._backpropagate(path, reward)

    def _select(self, root_node: Any, game: AlignQuattroGame) -> list[Any]:
        """Return the path selected during the selection phase of MCTS.

        Starting at the root_node, repeatedly choose the child with the highest UCB score until reaching either a
        terminal node or a node with an unexplored legal move. The same moves are applied to game so that game stays in
        sync with the final node in the returned path.

        Preconditions:
            - game.get_outcome() in {'in progress', 'red win', 'yellow win', 'tie'}

        >>> game = AlignQuattroGame()
        >>> player = MCTSPlayer()
        >>> path = player._select(None, game)   # doctest: +SKIP
        >>> isinstance(path, list)              # doctest: +SKIP
        True
        """
        current_node = root_node
        path = [current_node]

        while game.get_outcome() == "in progress":
            legal_moves = game.get_available_columns()
            # We must expand all moves eventually. Hence, if the number of unexpanded moves is not yet
            # the total possible number of moves at this node, stop this loop and expand one unexplored child.
            if len(current_node.children) < len(legal_moves):
                break

            move, next_node = self._find_best_child(current_node)

            game.make_move(move)
            current_node = next_node
            path.append(current_node)

        return path

    def _expand(self, node: Any, game: AlignQuattroGame) -> Any:
        """Expand node by adding one previously unexplored legal move to the search tree/DAG.

        One legal move that is not already in node.children is chosen at random, then the move is applied to game, the
        corresponding child node is created (or retrieved, if DAG search), and the child is stored in node.children.

        Preconditions:
            - game.get_outcome() == 'in progress'

        >>> game = AlignQuattroGame()
        >>> player = MCTSPlayer()
        >>> child = player._expand(None, game)   # doctest: +SKIP
        """
        legal_moves = game.get_available_columns()
        unexplored_legal_moves = [legal_move for legal_move in legal_moves if legal_move not in node.children]
        # Randomly chooses an unexplored legal move
        chosen_move = random.choice(unexplored_legal_moves)
        # Mutates the copy of the game object, in order to create the new node
        game.make_move(chosen_move)

        if self.is_dag:
            child_node = self._retrieve_or_create_dag_node(game)
        else:
            child_node = _TreeNode()

        node.children[chosen_move] = child_node
        return child_node

    def _simulate(self, game: AlignQuattroGame, root_is_red: bool) -> float:
        """Play random moves until the game terminates (ends in a player winning or a tie) and returns the resulting
        reward. The reward is calculated based on the perspective of the player at the root of the search, with
        1.0 for a root player win, 0.0 for a draw, and -1.0 if the root player loses.

        Preconditions:
            - game.get_outcome() in {'in progress', 'red win', 'yellow win', 'tie'}

        >>> game = AlignQuattroGame()
        >>> player = MCTSPlayer()
        >>> reward = player._simulate(game, True)   # doctest: +SKIP
        >>> reward in {-1.0, 0.0, 1.0}              # doctest: +SKIP
        True
        """
        simulated_game = copy.deepcopy(game)
        while simulated_game.get_outcome() == "in progress":
            # These two lines keep making random moves on the copied game object until the game terminates
            chosen = random.choice(simulated_game.get_available_columns())
            simulated_game.make_move(chosen)

        return self._reward_from_simulation(simulated_game.get_outcome(), root_is_red)

    def _backpropagate(self, path: list[Any], reward: float) -> None:
        """Update visit counts and value sums along the visited path.

        Each node in the path has its visit count increased by 1. The reward is added to value_sum. Note that the sign
        of reward flips after each step going up the path, as the perspective changes for different players.

        Preconditions:
            - all(node is not None for node in path)
            - reward in {-1.0, 0.0, 1.0}
        """
        for node in reversed(path):
            node.visit_count += 1
            node.value_sum += reward
            reward = -reward

    def _find_best_child(self, node: Any) -> tuple[int, Any]:
        """Return the (move, child) tuple with the highest UCB score.

        This helper is used during selection phase (Step 2 of the MCTS), rather than the final selection of the move.

        Preconditions:
            - len(node.children) > 0
        """
        best_move_so_far = -1
        best_child_so_far = None
        best_score_so_far = -math.inf

        for move, child in node.children.items():     # Extracts the key-value pair
            score = self._ucb_score(node, child)
            # Updates the best score so far if it surpasses the current best score
            if best_score_so_far < score:
                best_score_so_far = score
                best_move_so_far = move
                best_child_so_far = child

        return (best_move_so_far, best_child_so_far)

    def _ucb_score(self, parent: Any, child: Any) -> float:
        """Return the UCB score of a child, relative to its parent.

        The larger the score, the more indication that the child should be explored next.

        Preconditions:
            - parent is not None
            - child is not None

        >>> player = MCTSPlayer()
        >>> score = player._ucb_score(None, None)   # doctest: +SKIP
        >>> isinstance(score, float)                # doctest: +SKIP
        True
        """
        if child.visit_count == 0:
            return float('inf')
        elif parent.visit_count == 0:
            return float('inf')

        exploit_term = -(child.value_sum / child.visit_count)
        exploration_term = self.exploration_weight * math.sqrt(math.log(parent.visit_count) / child.visit_count)
        return exploit_term + exploration_term

    def _choose_final_move(self, root_node: Any) -> int:
        """Return the move chosen after all search iterations are complete.

        The selected move is the one whose child has the greatest visit count. The child with the highest visit count
        will be chosen.

        Preconditions:
            - len(root_node.children) > 0

        >>> player = MCTSPlayer()
        >>> isinstance(player._choose_final_move(None), int)   # doctest: +SKIP
        True
        """
        optimal_move_so_far = -1
        most_visited_move_so_far = -1

        for move, child in root_node.children.items():
            if child.visit_count > most_visited_move_so_far:
                most_visited_move_so_far = child.visit_count
                optimal_move_so_far = move

        return optimal_move_so_far

    def _promote_child_to_root(self, current_root: Any, real_move: int) -> None:
        """Update this player's stored root after a real move is played.

        If move is already among current_root.children, this method can preserve the corresponding child as the new
        root so past search statistics can be reused on future turns. It updates the new root to be the child of the
        original. If real_move is not legal or current root is None, it resets the root to be None.

        Preconditions:
            - 0 <= real_move <= 6

        >>> player = MCTSPlayer()
        >>> player._promote_child_to_root(None, 3)
        >>> player._root is None
        True
        """
        if current_root is not None and real_move in current_root.children:
            self._root = current_root.children[real_move]
        else:
            self._root = None

    def _reward_from_simulation(self, outcome: str, root_is_red: bool) -> float:
        """Convert a terminal game outcome from a rollout / simulation into a rollout reward, in order for
        backpropagation (Step 4 of the MCTS process). Again, the reward is measured based on the perspective of the
        player at the root of the search.

        Preconditions:
            - outcome in {'red win', 'yellow win', 'tie'}

        >>> player = MCTSPlayer()
        >>> player._reward_from_simulation('tie', True)
        0.0
        >>> player._reward_from_simulation('red win', True)
        1.0
        >>> player._reward_from_simulation('red win', False)
        -1.0
        """
        # Reward for tie is 0.0 (stalemate)
        if outcome == 'tie':
            return 0.0
        elif outcome == 'red win':
            if root_is_red:
                return 1.0
            else:
                return -1.0
        else:
            if root_is_red:
                return -1.0
            else:
                return 1.0

    def _root_player_is_red(self, game: AlignQuattroGame) -> bool:
        """Return whether the player to move in game is red.

        >>> game = AlignQuattroGame()
        >>> player = MCTSPlayer()
        >>> player._root_player_is_red(game)   # doctest: +SKIP
        True
        """
        return game.is_red_turn()

    def _retrieve_or_create_dag_node(self, game: AlignQuattroGame) -> DAGNode:
        """Return the DAG node representing the AlignQuattroGame object game.

        If this board state has already been seen, return the existing shared node. Otherwise, create a new node,
        store it in the transposition table, and return it.

        Preconditions:
            - self.is_dag

        >>> player = MCTSPlayer()
        >>> player.is_dag = True
        >>> game = AlignQuattroGame()
        >>> node1 = player._retrieve_or_create_dag_node(game)   # doctest: +SKIP
        >>> node2 = player._retrieve_or_create_dag_node(game)   # doctest: +SKIP
        >>> node1 is node2                                      # doctest: +SKIP
        True
        """
        state_hash = zobrist_hash(game)
        return get_or_create_node(state_hash, self._transposition_table)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': [
            'math', 'random', 'typing', 'copy', 'dataclasses',
            'game_logic', 'mcts_dag'
        ],
        'allowed-io': [],
        'max-line-length': 120,
        'disable': ['too-many-instance-attributes']
    })
