###################################
# Test Move generator efficiency and correctness on position
###################################

from BitPosition import BitPosition
from utils import board_to_bitboards, bitposition_to_chessboard, compare_dicts, bitposition_to_fen
import time
import chess
import subprocess
import stockfish
import re

def run_stockfish_perft(fen, depth):
    # Path to your Stockfish executable
    stockfish_path = '/opt/homebrew/bin/Stockfish'
    
    # Start Stockfish process
    process = subprocess.Popen(stockfish_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)

    # Send UCI commands to Stockfish
    process.stdin.write('uci\n')
    process.stdin.write('position fen ' + fen + '\n')
    process.stdin.write('go perft ' + str(depth) + '\n')
    process.stdin.flush()

    # Process the output
    perft_results = {}
    total_nodes = 0
    move_pattern = re.compile(r'([a-h][1-8])([a-h][1-8]): (\d+)')

    while True:
        line = process.stdout.readline().strip()
        if line:
            match = move_pattern.search(line)
            if match:
                from_square, to_square = match.groups()[:2]
                leaf_nodes = int(match.group(3))
                from_index = (int(from_square[1]) - 1) * 8 + (ord(from_square[0]) - ord('a'))
                to_index = (int(to_square[1]) - 1) * 8 + (ord(to_square[0]) - ord('a'))
                perft_results[(from_index, to_index)] = leaf_nodes
        if 'Nodes searched' in line:
            total_nodes = int(line.split(': ')[1])
            break

    process.stdin.write('quit\n')
    process.stdin.flush()
    process.terminate()

    return perft_results, total_nodes

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
    fen = bitposition_to_fen(bitposition)
    print(fen)
    stockfish_perft_results, total_nodes = run_stockfish_perft(fen, depth)
    
    # Calculate our perft results
    start_time = time.time()
    num_positions, our_leaf_nodes =  move_maker_v2(bitposition, depth, depth)
    time_taken = time.time()-start_time
    
    moves_we_dont_have, moves_we_should_not_have, differing_moves = compare_dicts(stockfish_perft_results, our_leaf_nodes)
    return {'Number of positions we get': num_positions, 'Time taken': time_taken, 'Number of positions we should get': total_nodes, 'Moves that differ in count': differing_moves, "Moves that we don't have": moves_we_dont_have, "Moves we shouldnt have": moves_we_should_not_have}

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
