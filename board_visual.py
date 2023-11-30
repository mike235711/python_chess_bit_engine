import pygame
import sys

from BitPosition import Move, BitPosition
from utils import board_to_bitboards, bitboards_to_board

# Example move generator function (replace with your actual function)
def generate_valid_moves(position):
    non_capture_moves = position.non_capture_moves()
    capture_moves = position.capture_moves()
    return list(non_capture_moves) + list(capture_moves)

def generate_valid_moves_in_check(position):
    in_check_moves = position.in_check_moves()
    return list(in_check_moves)

def draw_board(screen, board, dragged_piece, mouse_pos):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    square_size = 60  # size of each square

    # Load images of chess pieces
    pieces_images = load_pieces_images(square_size)

    # Draw squares and pieces
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, (col*square_size, row*square_size, square_size, square_size))
            piece = board[row * 8 + col]
            if piece != '0':
                if piece.isupper():
                    piece_image = 'w'+piece
                else:
                    piece_image = piece
                screen.blit(pieces_images[piece_image], (col*square_size, row*square_size))
    
    # Draw the dragged piece at the mouse position if there is one
    if dragged_piece:
        piece_image, piece_rect = dragged_piece
        piece_rect.center = mouse_pos
        screen.blit(piece_image, piece_rect)

def load_pieces_images(square_size):
    pieces_im = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wP', 'r', 'n', 'b', 'q', 'k', 'p']
    images = {}
    for piece_im in pieces_im:
        images[piece_im] = pygame.transform.scale(pygame.image.load(f"images/{piece_im}.png"), (square_size, square_size))
    return images

def get_square_at_pos(pos, square_size):
    x, y = pos
    row = y // square_size
    col = x // square_size
    return row, col

import pygame
import sys
# Import other necessary modules or functions

def main():
    pygame.init()
    screen = pygame.display.set_mode((480, 480))
    pygame.display.set_caption("Chess Board")
    square_size = 60

    # Define initial variables
    selected_piece = None
    selected_pos = None
    dragged_piece = None

    # Define the initial board state
    board = [
        'wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR',
        'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
        'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'
    ]

    pieces_images = load_pieces_images(square_size)
    position = BitPosition(board_to_bitboards(board), -1, wc=True, bc=True, turn=True, in_check=False, unsafe_squares=0)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                selected_pos = get_square_at_pos(mouse_pos, square_size)
                selected_piece = board[selected_pos[0] * 8 + selected_pos[1]]
                if selected_piece != '0':
                    dragged_piece = (pieces_images[selected_piece], pieces_images[selected_piece].get_rect(topleft=mouse_pos))
                    board[selected_pos[0] * 8 + selected_pos[1]] = '0'
            elif e.type == pygame.MOUSEBUTTONUP:
                if dragged_piece:
                    new_pos = get_square_at_pos(mouse_pos, square_size)
                    from_index = selected_pos[0] * 8 + selected_pos[1]
                    to_index = new_pos[0] * 8 + new_pos[1]
                    if not position.in_check:
                        valid_moves = list(generate_valid_moves(position))
                    else:
                        print('In check')
                        valid_moves = list(generate_valid_moves_in_check(position))
                    print(position.bitboard)
                    print(valid_moves)
                    move_valid = False

                    for move in valid_moves:
                        if move.i == from_index and move.j == to_index:
                            move_valid = True
                            position = position.move(move)
                            break

                    if move_valid:
                        board = bitboards_to_board(position.bitboard, position.turn)
                        board[to_index] = selected_piece
                    else:
                        board[from_index] = selected_piece  # Revert to original position

                    dragged_piece = None
                    selected_piece = None

        draw_board(screen, board, dragged_piece, mouse_pos)
        pygame.display.flip()

if __name__ == "__main__":
    main()
