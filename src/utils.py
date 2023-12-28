import chess
import numpy as np

def bit_to_numpy_array(bit):
    array = np.zeros(64, dtype=int)
    for i in range(64):
        array[i] = (bit >> i) & 1
    return array[::-1]

def compare_dicts(dict1, dict2):
    # Find keys that are only in dict1
    only_in_dict1 = {k: dict1[k] for k in dict1 if k not in dict2}

    # Find keys that are only in dict2
    only_in_dict2 = {k: dict2[k] for k in dict2 if k not in dict1}

    # Find keys that are in both but have different values
    different_values = {k: (dict1[k], dict2[k]) for k in dict1 if k in dict2 and dict1[k] != dict2[k]}

    return only_in_dict1, only_in_dict2, different_values

def bitposition_to_chessboard(bitposition):
    board = chess.Board(None)  # Create an empty board

    piece_symbols = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
    
    # Iterate through each bitboard and set pieces on the board
    for i, bitboard in enumerate(bitposition.bitboard):
        # For each square, check if there's a piece and place it
        for square in range(64):
            if bitboard & (1 << square):
                board.set_piece_at(chess.SQUARES[square], chess.Piece.from_symbol(piece_symbols[i]))

    # Set the turn
    board.turn = chess.WHITE if bitposition.turn else chess.BLACK

    # Set castling rights
    board.castling_rights = 0
    if bitposition.wc[0]:
        board.castling_rights |= chess.BB_H1
    if bitposition.wc[1]:
        board.castling_rights |= chess.BB_A1
    if bitposition.bc[0]:
        board.castling_rights |= chess.BB_H8
    if bitposition.bc[1]:
        board.castling_rights |= chess.BB_A8

    # Set en passant square
    if bitposition.psquare != -1:
        board.ep_square = chess.square(bitposition.psquare % 8, bitposition.psquare // 8)

    return board

def bitposition_to_fen(bitposition):
    # Mapping of piece types to their representations
    pieces = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']

    # Generate the 8x8 board representation
    board = [''] * 64
    for i, bitboard in enumerate(bitposition.bitboard):
        for j in range(64):
            if bitboard & (1 << j):
                board[j] = pieces[i]

    # Convert board to FEN string
    fen_rows = []
    for row in range(8):
        empty_count = 0
        fen_row = ''
        for col in range(8):
            piece = board[(7-row) * 8 + col]
            if piece:
                if empty_count:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += piece
            else:
                empty_count += 1
        if empty_count:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)
    fen_board = '/'.join(fen_rows)

    # Turn
    turn = 'w' if bitposition.turn else 'b'

    # Castling rights
    wc = ''.join(['K' if bitposition.wc[0] else '', 'Q' if bitposition.wc[1] else ''])
    bc = ''.join(['k' if bitposition.bc[0] else '', 'q' if bitposition.bc[1] else ''])
    castling_rights = wc + bc or '-'

    # En passant target square
    if bitposition.psquare != -1:
        file = chr((bitposition.psquare % 8) + ord('a'))
        rank = str(8 - (bitposition.psquare // 8))
        ep_square = file + rank
    else:
        ep_square = '-'

    return f'{fen_board} {turn} {castling_rights} {ep_square} 0 1'  # Assuming halfmove and fullmove are set to default values

def has_one_one(n):
    count = 0
    while n:
        n &= (n - 1)  # Flip the least significant 1 bit of n to 0
        count += 1
        if count > 1:
            return False
    if count == 1:
        return True
    return False


def get_set_bit_indices(bit):
    # Get the indices of the ones in a bit
    indices = []
    index = 0
    while bit:
        if bit & 1:
            yield index
        index += 1
        bit >>= 1

def find_least_significant_bit_set(bitboard):
    if bitboard == 0:
        return -1  # No bits are set
    position = 0
    while (bitboard & 1) == 0:
        bitboard >>= 1
        position += 1
    return position

def board_to_bitboards(board):
    """
    Convert a standard board representation to a set of bitboards.

    Parameters:
    board (list): A list of 64 characters representing the board state.

    Returns:
    dict: A dictionary of bitboards for each piece type.
    """
    # Define piece types
    pieces = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']

    # Initialize bitboards
    bitboards = {piece: 0 for piece in pieces}

    for board_index, square in enumerate(board):
        if square in pieces:
            # Set the bit at the correct position
            #board_row = board_index // 8
            #board_column = board_index % 8
            #board_index = board_row * 8 + (7- board_column)
            bitboards[square] |= 1 << board_index

    return list(bitboards.values())


def bitboards_to_board(bitboards):
    """
    Convert a set of bitboards to a standard board representation.
    Returns:
    list: A list of 64 characters representing the board state.
    """
    # Create an empty board
    pieces_1 = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']
    board = ['0'] * 64
    for piece_index, bitboard in enumerate(bitboards): # w_pawns, w_knights, w_bishops, w_rooks, w_queens, w_king, ...
        for i in range(64):
            if bitboard & (1 << (i)):
                #board_row = i // 8
                #board_column = 7-(i % 8)
                #board_index = board_row * 8 + board_column
                board[i] = pieces_1[piece_index]
    return board


def generate_knight_moves(square): # Crawler (bitboard for all squares)
    moves = 0
    r, c = divmod(square, 8)
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    for dr, dc in knight_moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            moves |= 1 << (nr * 8 + nc)
    return moves

def generate_king_moves(square):
    moves = 0
    r, c = divmod(square, 8)
    king_moves = [(1, 0), (1, 1), (1, -1), (0, 1), (0, -1), (-1, 0), (-1, 1), (-1, -1)]
    for dr, dc in king_moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            moves |= 1 << (nr * 8 + nc)
    return moves

def generate_pawn_moves(square, color='white'): # Crawler (bitboard for all squares)
    '''
    Generate pawn bits without taking into account double moves
    '''
    moves = 0
    r, c = divmod(square, 8)
    if color == 'white':
        if 0 < r < 7:  # Pawns cannot move forward on the last rank and are never on the first
            moves |= 1 << ((r + 1) * 8 + c)
    else:  # Black pawn
        if 7 > r > 0:  # Pawns cannot move forward on the first rank and are never on the first
            moves |= 1 << ((r - 1) * 8 + c)
    return moves

def generate_pawn_attack_moves(square, color='white'):
    attacks = 0
    r, c = divmod(square, 8)

    if color == 'white':
        if 0 <= r < 7:  # Pawns cannot attack from the last rank and are never on the first
            if c > 0:  # Capture to the left
                attacks |= 1 << ((r + 1) * 8 + (c - 1))
            if c < 7:  # Capture to the right
                attacks |= 1 << ((r + 1) * 8 + (c + 1))
    elif color == 'black':  # Black pawn
        if 7 >= r > 0:  # Pawns cannot attack from the first rank and are never on the last
            if c > 0:  # Capture to the left
                attacks |= 1 << ((r - 1) * 8 + (c - 1))
            if c < 7:  # Capture to the right
                attacks |= 1 << ((r - 1) * 8 + (c + 1))

    return attacks



def generate_rook_unfull_rays(square):
    '''
    Generating rook ray masks, however the rays end just before reaching the board border (unless already at the border).
    '''
    moves = 0
    r, c = divmod(square, 8)
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # vertical and horizontal
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if r == 0 and c == 0:  # Then we can go to the 1st row and 1st column, but not the 8th row or 8th column
            while 0 <= nr < 7 and 0 <= nc < 7:
                moves |= 1 << (nr * 8 + nc)
                nr += dr
                nc += dc
        elif r == 0 and c == 7:
            while 0 <= nr < 7 and 0 < nc <= 7:
                moves |= 1 << (nr * 8 + nc)
                nr += dr
                nc += dc
        elif r == 7 and c == 0:
            while 0 < nr <= 7 and 0 <= nc < 7:
                moves |= 1 << (nr * 8 + nc)
                nr += dr
                nc += dc
        elif r == 7 and c == 7:
            while 0 < nr <= 7 and 0 < nc <= 7:
                moves |= 1 << (nr * 8 + nc)
                nr += dr
                nc += dc
        elif r == 0: 
            while 0 <= nr < 7 and 0 < nc < 7:
                moves |= 1 << (nr * 8 + nc)
                nr += dr
                nc += dc
        elif r == 7: 
            while 0 < nr <= 7 and 0 < nc < 7:
                moves |= 1 << (nr * 8 + nc)
                nr += dr
                nc += dc
        elif c == 0: 
            while 0 < nr < 7 and 0 <= nc < 7:
                moves |= 1 << (nr * 8 + nc)
                nr += dr
                nc += dc
        elif c == 7: 
            while 0 < nr < 7 and 0 < nc <= 7:
                moves |= 1 << (nr * 8 + nc)
                nr += dr
                nc += dc
        else:
            while 0 < nr < 7 and 0 < nc < 7:
                moves |= 1 << (nr * 8 + nc)
                nr += dr
                nc += dc
    return moves

def generate_bishop_unfull_rays(square):
    '''
    Generating bishop rays that finish just before reaching the border.
    '''
    moves = 0
    r, c = divmod(square, 8)
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # diagonals
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while 0 < nr < 7 and 0 < nc < 7:
            moves |= 1 << (nr * 8 + nc)
            nr += dr
            nc += dc
    return moves


def generate_queen_unfull_rays(square):
    # Combine rook and bishop moves
    return generate_rook_unfull_rays(square) | generate_bishop_unfull_rays(square)

def generate_rook_full_rays(square):
    '''
    Generating rook ray masks, however the rays end just before reaching the board border (unless already at the border).
    '''
    moves = 0
    r, c = divmod(square, 8)
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # vertical and horizontal
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while 0 <= nr <= 7 and 0 <= nc <= 7:
            moves |= 1 << (nr * 8 + nc)
            nr += dr
            nc += dc
        
    return moves

def generate_bishop_full_rays(square):
    '''
    Generating bishop rays that finish just before reaching the border.
    '''
    moves = 0
    r, c = divmod(square, 8)
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # diagonals
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while 0 <= nr <= 7 and 0 <= nc <= 7:
            moves |= 1 << (nr * 8 + nc)
            nr += dr
            nc += dc
    return moves

def generate_queen_full_rays(square):
    # Combine rook and bishop moves
    return generate_rook_full_rays(square) | generate_bishop_full_rays(square)


def visualize_bitboard(bitboard):
    board_representation = ""
    for r in range(8):
        for c in range(8):
            if bitboard & (1 << ((7-r) * 8 + c)):
                board_representation += '1 '
            else:
                board_representation += '. '
        board_representation += '\n'
    return board_representation


def generate_bit_combinations(square, piece_type):
    '''
    Get all the blocker configurations given a piece and square.
    '''
    if piece_type == 'R':
        ray_mask = generate_rook_unfull_rays(square)
    elif piece_type == 'B':
        ray_mask = generate_bishop_unfull_rays(square)
    else:
        return 'piece type should be either R or B'

    def generate_combinations(n, current=0, pos=0):
        if pos < 64:
            # Recurse without changing the current bit
            yield from generate_combinations(n, current, pos + 1)
            # Recurse with the current bit toggled if it is set in n
            if n & (1 << pos):
                yield from generate_combinations(n, current | (1 << pos), pos + 1)
        else:
            # Yield the combination
            yield current

    return list(generate_combinations(ray_mask))

def generate_two_bit_combinations(bit):
    '''
    Generate all combinations of the given bit with exactly two '1's.
    '''

    def generate_combinations(n, current=0, pos=0, count=0):
        if pos < 64:
            # Recurse without changing the current bit
            yield from generate_combinations(n, current, pos + 1, count)
            # Recurse with the current bit toggled if it is set in n
            if n & (1 << pos):
                yield from generate_combinations(n, current | (1 << pos), pos + 1, count + 1)
        elif count == 2:
            # Yield the combination only if it has exactly two '1's
            yield current

    yield from generate_combinations(bit)

def generate_one_bit_combinations(bit):
    '''
    Generate all combinations of the given bit with exactly one '1's.
    '''

    def generate_combinations(n, current=0, pos=0, count=0):
        if pos < 64:
            # Recurse without changing the current bit
            yield from generate_combinations(n, current, pos + 1, count)
            # Recurse with the current bit toggled if it is set in n
            if n & (1 << pos):
                yield from generate_combinations(n, current | (1 << pos), pos + 1, count + 1)
        elif count == 1:
            # Yield the combination only if it has exactly two '1's
            yield current

    yield from generate_combinations(bit)



def get_valid_piece_moves(square, piece_type, blockers):
    """
    Generates possible moves for a rook or a bishop on a given square with blockers that we cannot capture.
    """
    def ray_moves(square, direction):
        moves = 0
        r, c = divmod(square, 8)
        dr, dc = direction
        nr, nc = r + dr, c + dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            index = nr * 8 + nc
            if blockers & (1 << index):
                # Stop if a blocker is encountered
                break
            moves |= 1 << index
            nr += dr
            nc += dc
        return moves

    if piece_type == 'R':
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # vertical and horizontal
    elif piece_type == 'B':
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # diagonals
    else:
        return 'piece type should be either R or B'

    possible_moves = 0
    for direction in directions:
        possible_moves |= ray_moves(square, direction)

    return possible_moves

def get_valid_piece_moves_including_captures(square, piece_type, blockers):
    """
    Generates possible moves for a rook or a bishop on a given square with blockers that we cannot capture.
    """
    def ray_moves(square, direction):
        moves = 0
        r, c = divmod(square, 8)
        dr, dc = direction
        nr, nc = r + dr, c + dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            index = nr * 8 + nc
            if blockers & (1 << index):
                # Stop if a blocker is encountered
                moves |= 1 << index
                break
            moves |= 1 << index
            nr += dr
            nc += dc
        return moves

    if piece_type == 'R':
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # vertical and horizontal
    elif piece_type == 'B':
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # diagonals
    else:
        return 'piece type should be either R or B'

    possible_moves = 0
    for direction in directions:
        possible_moves |= ray_moves(square, direction)

    return possible_moves

def get_valid_piece_moves_including_captures_one_blocker(square, piece_type, blockers):
    """
    Generates possible moves for a rook or a bishop on a given square with blockers that we cannot capture.
    """
    def ray_moves(square, direction):
        moves = 0
        r, c = divmod(square, 8)
        dr, dc = direction
        nr, nc = r + dr, c + dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            index = nr * 8 + nc
            if blockers & (1 << index):
                # Stop if a blocker is encountered
                moves |= 1 << index
                break
            moves |= 1 << index
            nr += dr
            nc += dc
        return moves

    if piece_type == 'R':
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # vertical and horizontal
    elif piece_type == 'B':
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # diagonals
    else:
        return 'piece type should be either R or B'

    possible_moves = 0
    for direction in directions:
        possible_moves |= ray_moves(square, direction)

    return possible_moves


def get_ordered_blockers(square, piece_type):
    '''
    Get a list of tuples where each tuple consists of blocker bits which lead to the same valid moves in the end.
    '''
    if piece_type == 'R':
        unordered_blockers = generate_bit_combinations(square, piece_type)
    elif piece_type == 'B':
        unordered_blockers = generate_bit_combinations(square, piece_type)
    else:
        return 'piece type shoud be either R or B'
    ordered_blockers = []
    for blockers_bit_1 in unordered_blockers:
        if blockers_bit_1 in [item for row in ordered_blockers for item in row]:
            continue
        else: 
            new_blocker_group = [blockers_bit_1]
        for blockers_bit_2 in unordered_blockers:
            if blockers_bit_1 == blockers_bit_2:
                continue
            valid_moves_1 = get_valid_piece_moves(square, piece_type, blockers_bit_1)
            valid_moves_2 = get_valid_piece_moves(square, piece_type, blockers_bit_2)
            if valid_moves_1 == valid_moves_2:
                new_blocker_group.append(blockers_bit_2)
        ordered_blockers.append(new_blocker_group)
    return ordered_blockers


