###################################
# Test Move generator efficiency and correctness on position
###################################

from BitPosition import BitBoard, BitPosition
from utils import board_to_bitboards
import time

board = [
    'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R',
    'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
    '0', '0', '0', '0', '0', '0', '0', '0',
    '0', '0', '0', '0', '0', '0', '0', '0',
    '0', '0', '0', '0', '0', '0', '0', '0',
    '0', '0', '0', '0', '0', '0', '0', '0',
    'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
    'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'
]

def test_generator_correctness(board, depth, turn):
    bitboards_array = board_to_bitboards(board)
    bitboard = BitBoard(bitboards_array)
    bitposition = BitPosition(bitboard, psquare = None, wc = True, bc = True, history = [], turn = turn)
    start_time = time.time()
    num_positions =  move_maker(bitposition, depth)
    time_taken = time.time()-start_time
    return {'Number of positions': num_positions, 'Time taken': time_taken}

def move_maker(bitposition, depth, count = 0):
    # Works fine
    if depth == 0:
        return count

    for move in bitposition.get_moves():
        count += 1
        bitposition.move(move)
        count = move_maker(bitposition, depth-1, count)
        bitposition.pop()
    return count