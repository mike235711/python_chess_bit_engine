###################################
# Test Move generator efficiency and correctness on position
###################################

from BitPosition import BitPosition
from utils import board_to_bitboards, bitposition_to_chessboard, compare_dicts
import time
import chess

def number_of_leaves(bitposition, depth):
    start_time = time.time()
    num_positions =  move_maker(bitposition, depth)
    time_taken = time.time()-start_time
    return {'Number of positions': num_positions, 'Time taken': time_taken}

def move_maker(bitposition, depth, count = 0):
    # Works fine
    if depth == 0:
        return count
    if not bitposition.is_check():
        valid_moves = list(bitposition.capture_moves()) + list(bitposition.non_capture_moves())
    else:
        valid_moves = list(bitposition.in_check_captures()) + list(bitposition.in_check_moves())

    for move in valid_moves:
        if depth == 1:
            count += 1
        bitposition.move(move)
        #print('Make move:', move)
        count = move_maker(bitposition, depth-1, count)
        #print('Unmake move:', move)
        bitposition.unmake_move(move)
    return count

def test_generator_correctness(bitposition, depth):
    # Calculate and print the real perft result for each initial move
    python_board = bitposition_to_chessboard(bitposition)
    initial_move_results = perft_initial_moves(python_board, depth)
    total_nodes = sum(initial_move_results.values())

    for move, nodes in initial_move_results.items():
        print(f"{move}: {nodes}")
    
    # Calculate our perft results
    start_time = time.time()
    num_positions, our_leaf_nodes =  move_maker_v2(bitposition, depth, depth)
    time_taken = time.time()-start_time
    for move, nodes in our_leaf_nodes.items():
        print(f"{move}: {nodes}")
    
    _, _, differing_moves = compare_dicts(initial_move_results, our_leaf_nodes)
    return {'Number of positions we get': num_positions, 'Time taken': time_taken, 'Number of positions we should get': total_nodes, 'Moves that differ in count': differing_moves}

def move_maker_v2(bitposition, depth, initial_depth, leaf_nodes=None):
    if depth == 0:
        return 1, 'klk'  # Return 1 for each leaf node
    if leaf_nodes is None and depth == initial_depth:
        leaf_nodes = {}  # Initialize dictionary to store leaf nodes count for each starting move

    if not bitposition.is_check():
        valid_moves = list(bitposition.capture_moves()) + list(bitposition.non_capture_moves())
    else:
        valid_moves = list(bitposition.in_check_captures()) + list(bitposition.in_check_moves())

    count = 0
    for move in valid_moves:
        bitposition.move(move)  # Make the move
        leaf_count, _ = move_maker_v2(bitposition, depth-1, initial_depth, leaf_nodes)
        count += leaf_count

        if depth == initial_depth:
            leaf_nodes[(move.i, move.j)] = leaf_count  # Store the leaf node count for the initial move
        
        bitposition.unmake_move(move)  # Unmake the move

    return count, leaf_nodes



def perft(board, depth):
    if depth == 0:
        return 1

    nodes = 0
    for move in board.legal_moves:
        board.push(move)
        nodes += perft(board, depth - 1)
        board.pop()
    
    return nodes

def perft_initial_moves(board, depth):
    initial_moves = {}
    for move in board.legal_moves:
        board.push(move)
        nodes = perft(board, depth - 1)
        board.pop()
        initial_moves[(board.parse_san(board.san(move)).from_square, board.parse_san(board.san(move)).to_square)] = nodes

    return initial_moves
