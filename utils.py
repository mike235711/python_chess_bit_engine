import numpy as np

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

    for i, square in enumerate(board):
        if square in pieces:
            # Set the bit at the correct position
            bitboards[square] |= 1 << (i)

    return list(bitboards.values())


def bitboards_to_board(bitboards, turn):
    """
    Convert a set of bitboards to a standard board representation.
    Returns:
    list: A list of 64 characters representing the board state.
    """
    # Create an empty board
    pieces_1 = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']
    pieces_2 = ['bP', 'bN', 'bB', 'bR', 'bQ', 'bK', 'wP', 'wN', 'wB', 'wR', 'wQ', 'wK']
    board = ['0'] * 64
    if turn:
        for piece_index, bitboard in enumerate(bitboards): # w_pawns, w_knights, w_bishops, w_rooks, w_queens, w_king, ...
            for i in range(64):
                if bitboard & (1 << (i)):
                    board[i] = pieces_1[piece_index]
    else:
        for piece_index, bitboard in enumerate(bitboards): # b_pawns, b_knights, b_bishops, b_rooks, b_queens, b_king, ...
            for i in range(64):
                if bitboard & (1 << (i)):
                    board[i] = pieces_2[piece_index]
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
    moves = 0
    r, c = divmod(square, 8)
    if color == 'white':
        if r < 7:  # Pawns cannot move forward on the last rank
            moves |= 1 << ((r + 1) * 8 + c)
            if r == 1:  # Double move from starting position
                moves |= 1 << ((r + 2) * 8 + c)
    else:  # Black pawn
        if r > 0:  # Pawns cannot move forward on the first rank
            moves |= 1 << ((r - 1) * 8 + c)
            if r == 6:  # Double move from starting position
                moves |= 1 << ((r - 2) * 8 + c)
    return moves

def generate_pawn_attack_moves(square, color='white'):
    attacks = 0
    r, c = divmod(square, 8)

    if color == 'white':
        if r < 7:  # Pawns cannot attack from the last rank
            if c > 0:  # Capture to the left
                attacks |= 1 << ((r + 1) * 8 + (c - 1))
            if c < 7:  # Capture to the right
                attacks |= 1 << ((r + 1) * 8 + (c + 1))
    elif color == 'black':  # Black pawn
        if r > 0:  # Pawns cannot attack from the first rank
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
            if bitboard & (1 << (r * 8 + c)):
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


