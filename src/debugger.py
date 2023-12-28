
from BitPosition import *
from utils import *

board = [
    'wR', '0', 'wB', 'wQ', 'wK', '0', 'wR', '0',
    'wP', 'wP', '0', '0', 'wB', 'wP', '0', '0',
    '0', '0', '0', 'wP', '0', '0', '0', 'bQ',
    '0', '0', 'wP', '0', '0', '0', '0', '0',
    '0', '0', '0', '0', '0', '0', 'wN', '0',
    '0', '0', 'bN', '0', 'bB', '0', '0', '0',
    'bP', 'bP', 'bP', '0', 'bP', 'bP', 'bP', 'bP',
    'bR', '0', '0', '0', 'bK', 'bB', '0', 'bR'
]
bitboards_array = board_to_bitboards(board)
position = BitPosition(bitboards_array, turn = False, wc = [False, True], bc = [True, True])
engine = Engine(evaluation_function_black)
engine_move = engine.Search(position, 2)[4]
print(engine_move)