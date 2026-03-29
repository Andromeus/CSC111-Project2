from __future__ import annotations
import math
import random
from typing import Any
import copy
import game_logic
from game_logic import Player, AlignQuattroGame
from mcts_dag import DAGNode, zobrist_hash, get_or_create_node
from dataclasses import dataclass, field

@dataclass
class _TreeNode:
    """A node in a tree-based MCTS search."""

    visit_count: int = 0
    value_sum: float = 0.0
    children: dict[int, "_TreeNode"] = field(default_factory=dict)


class MCTSPlayer(Player):
    """An AlignQuattro player that chooses moves using Monte Carlo Tree (or Graph) Search.

    This class is the Part B search layer. It assumes Part A provides:
        - a DAG node class storing visit_count, value_sum, and children
        - a function _get_or_create_node(game) that returns the shared node
          corresponding to the given game state

    Instance Attributes:
        - num_searches: the number of MCTS iterations to run before choosing a move
        - exploration_weight: the exploration constant c used in the UCB formula
        - is_dag: whether to run a dag MCTS search or a regular tree implementation
        - _root: the current root node for the preserved DAG, if any

    Representation Invariants:
        - self.num_searches >= 1
        - self.exploration_weight > 0
    """
    num_searches: int
    exploration_weight: float
    is_dag: bool
    self._transposition_table = {}
    _root: Any | None

    def __init__(self, num_searches: int = 400, exploration_weight: float = sqrt(2)) -> None:
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
        self.is_dag = True
        self._root = None

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

        It first obtains the root DAG node, and then repeats the steps of MCTS: selection, expansion, simulation,
        backpropagation, and then chooses the child move with the greatest visit count. Also, it can save the chosen
        child as the next root

        Preconditions:
            - root_game.get_outcome() == 'in progress'
            - len(root_game.get_available_columns()) > 0

        >>> game = AlignQuattroGame()
        >>> player = MCTSPlayer(5)
        >>> isinstance(player._mcts_search(game), int)   # doctest: +SKIP
        True
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
        """Run one complete MCTS iteration starting at the given root.

        A single iteration consists of:
            - selection
            - expansion (if non-terminal)
            - simulation
            - backpropagation

        root_game must not be mutated by callers after this method returns, so
        the implementation should work on a deep copy.

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
            expanded_child = self._expand(leaf, iter_game)
            path.append(expanded_child)

        root_is_red = self._root_player_is_red(root_game)
        reward = self._simulate(iter_game, root_is_red)
        self._backpropagate(path, reward)


    def _select(self, root_node: Any, game: AlignQuattroGame) -> list[Any]:
        """Traverse the DAG from root_node to a leaf and return the visited path.

        The returned list should contain the nodes visited in order, beginning
        with root_node and ending with the selected leaf. As this path is chosen,
        the same moves should be applied to game so that game stays synchronized
        with the final node in the path.

        A leaf for this method is any node where selection should stop, usually
        because the node is terminal or because not all legal moves have yet
        been expanded.

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
            if len(current_node.children) != len(legal_moves):
                break

            move, next_node = self._find_best_child(current_node)

            game.make_move(move)
            current_node = next_node
            path.append(current_node)

        return path


    def _expand(self, node: Any, game: AlignQuattroGame) -> Any:
        """Expand node by adding one previously unexpanded legal move.

        This method should:
            - find legal moves from game
            - determine which of them are not yet in node.children
            - choose one such move
            - apply it to game
            - obtain the child through Part A's _get_or_create_node(game)
            - store that child in node.children[move]
            - return the child node

        Preconditions:
            - game.get_outcome() == 'in progress'

        >>> game = AlignQuattroGame()
        >>> player = MCTSPlayer()
        >>> child = player._expand(None, game)   # doctest: +SKIP
        """
        legal_moves = game.get_available_columns()
        unexplored_legal_moves = [legal_move for legal_move in legal_moves if legal_move not in node.children]
        chosen_move = random.choice(unexplored_legal_moves)
        game.make_move(chosen_move)

        if self.is_dag:
            child_node = self._retrieve_or_create_dag_node(game)
        else:
            child_node = _TreeNode()

        node.children[move] = child_node
        return child_node

    def _simulate(self, game: AlignQuattroGame, root_is_red: bool) -> float:
        """Play a random rollout from game to a terminal outcome and return a reward.

        The reward is measured from the root player's perspective.
        Recommended convention:
            - 1.0 for a root-player win
            - 0.0 for a draw
            - -1.0 for a root-player loss

        This method should mutate only its local game copy.

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
            simulated_game.make_move(move)

        return self._reward_from_simulation(sim_game.get_outcome(), root_is_red)


    def _backpropagate(self, path: list[Any], reward: float) -> None:
        """Update visit counts and value sums along the visited path.

        The path must be the exact path traversed during this iteration.
        Because players alternate turns, many implementations negate the reward
        after each step while walking upward through the path.

        Preconditions:
            - all(node is not None for node in path)
            - reward in {-1.0, 0.0, 1.0}

        >>> player = MCTSPlayer()
        >>> player._backpropagate([], 0.0)
        """
        for node in reversed(path):
            node.visit_count += 1
            node.value_sum += reward
            reward = -reward


    def _find_best_child(self, node: Any) -> tuple[int, Any]:
        """Return the (move, child) pair with the highest UCB score.

        This helper is used during selection phase (Step 2 of the MCTS).

        Preconditions:
            - len(node.children) > 0

        >>> player = MCTSPlayer()
        >>> player._best_child(None)   # doctest: +SKIP
        (3, None)
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
        """Return the UCB score for child from parent.

        A standard choice is:
            Q(child) + c * sqrt(ln(N_parent) / N_child)

        Unvisited children are often treated as having infinite score so they
        are explored at least once.

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

        if parent.visit_count == 0:
            return float('inf')

        exploit_term = child.value_sum / child.visit_count
        exploration_term = self.exploration_weight * math.sqrt(math.log(parent.visit_count) / child.visit_count)
        return exploit_term + exploration_term


    def _choose_final_move(self, root_node: Any) -> int:
        """Return the move to play after step 3: search completes.

        The child with the highest visit count will be chosen, as this signifies the PUCT formula favors it the most.

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
        original. If real_move is not legal or current root is None, it initializes the root to be None.

        Preconditions:
            - 0 <= move <= 6

        >>> player = MCTSPlayer()
        >>> player._promote_child_to_root(None, 3)
        """
        if current_root is not None and real_move in current_root.children:
            self._root = current_root.children[real_move]
        else:
            self._root = None

    def _reward_from_simulation(self, outcome: str, root_is_red: bool) -> float:
        """Convert a terminal game outcome from a rollout / simulation into a rollout reward, in order for
        backpropagation (Step 4 of the MCTS process).

        Preconditions:
            - outcome in {'red win', 'yellow win', 'tie'}

        >>> player = MCTSPlayer()
        >>> player._reward_from_outcome('tie', True)
        0.0
        >>> player._reward_from_outcome('red win', True)
        1.0
        """
        # Reward for tie is 0.0 (stalemate)
        if outcome == 'tie':
            return 0.0
        #
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
        """Return the DAG node representing game.

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

# python_ta.check_all(config={
#     'extra-imports': [],  # the names (strs) of imported modules
#     'allowed-io': [],     # the names (strs) of functions that call print/open/input
#     'max-line-length': 120
# })
