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
                piece_image = piece
                screen.blit(pieces_images[piece_image], (col*square_size, row*square_size))
    
    # Draw the dragged piece at the mouse position if there is one
    if dragged_piece:
        piece_image, piece_rect = dragged_piece
        piece_rect.center = mouse_pos
        screen.blit(piece_image, piece_rect)

def load_pieces_images(square_size):
    pieces_im = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wP', 'bR', 'bN', 'bB', 'bQ', 'bK', 'bP']
    images = {}
    for piece_im in pieces_im:
        images[piece_im] = pygame.transform.scale(pygame.image.load(f"images/{piece_im}.png"), (square_size, square_size))
    return images

def get_square_at_pos(pos, square_size):
    x, y = pos
    row = y // square_size
    col = x // square_size
    return row, col

def draw_promotion_menu(screen, square_size, color):
    # Set the menu position to the right of the chessboard
    menu_x = 8 * square_size  # This places the menu just outside the 8x8 grid
    menu_y = square_size * 3  # Adjust this value to position the menu vertically
    menu_width = square_size * 2
    menu_height = square_size * 4  # Making the menu slightly taller to fit 4 options

    pygame.draw.rect(screen, pygame.Color("blue"), (menu_x, menu_y, menu_width, menu_height))

    pieces = ['wN', 'wB', 'wR', 'wQ'] if color == 'w' else ['bN', 'bB', 'bR', 'bQ']
    pieces_images = load_pieces_images(square_size)

    for i, piece in enumerate(pieces):
        piece_image = piece
        # Draw each piece option in the menu
        screen.blit(pieces_images[piece_image], (menu_x, menu_y + i * square_size))

    return pieces, menu_x, menu_y  # Return the menu position for mouse click handling



def main():
    pygame.init()
    square_size = 60
    board_width = square_size * 8
    menu_width = square_size * 2  # Width for the promotion menu
    screen = pygame.display.set_mode((board_width + menu_width, board_width))  # Increase the window width
    pygame.display.set_caption("Chess Board")

    # Define initial variables
    selected_piece = None
    selected_pos = None
    dragged_piece = None
    # Initialize promotion variables
    promoting = False
    promotion_row = promotion_col = None
    promotion_color = None
    promoting_moves = []

    # Define the initial board state
    board = [
        'wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR',
        'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        '0', '0', '0', '0', '0', '0', '0', '0',
        'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP',
        'bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR'
    ]

    pieces_images = load_pieces_images(square_size)
    position = BitPosition(board_to_bitboards(board), -1, wc=[True, True], bc=[True, True], turn=True)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                print(position.bitboard)
                selected_pos = get_square_at_pos(mouse_pos, square_size)
                selected_piece = board[selected_pos[0] * 8 + selected_pos[1]]
                if selected_piece != '0':
                    dragged_piece = (pieces_images[selected_piece], pieces_images[selected_piece].get_rect(topleft=mouse_pos))
                    board[selected_pos[0] * 8 + selected_pos[1]] = '0'
            elif e.type == pygame.MOUSEBUTTONUP:
                if promoting:
                    choice = None
                    pieces, menu_x, menu_y = draw_promotion_menu(screen, square_size, promotion_color)
                    mx, my = pygame.mouse.get_pos()
                    if menu_x <= mx < menu_x + square_size * 2:
                        for i in range(4):  # There are 4 pieces to choose from
                            piece_menu_y = menu_y + i * square_size
                            if piece_menu_y <= my < piece_menu_y + square_size:
                                choice = ['N', 'B', 'R', 'Q'][i]
                                break
                    if choice:
                        for move in promoting_moves:
                            if move.prom == {'N': 1, 'B': 2, 'R': 3, 'Q': 4}[choice]:
                                position = position.move(move)
                                board = bitboards_to_board(position.bitboard, position.turn)
                                board[to_index] = promotion_color + choice
                                break

                        promoting = False
                        promoting_moves = []
                else:
                    if dragged_piece:
                        new_pos = get_square_at_pos(mouse_pos, square_size)
                        from_index = selected_pos[0] * 8 + selected_pos[1]
                        to_index = new_pos[0] * 8 + new_pos[1]
                        if position.get_checks()[2] == 0:
                            valid_moves = list(generate_valid_moves(position))
                        else:
                            valid_moves = list(generate_valid_moves_in_check(position))
                        print(valid_moves)
                        move_valid = False
                        promoting_moves = []

                        for move in valid_moves:
                            if move.i == from_index and move.j == to_index and move.prom == 0:
                                move_valid = True
                                position = position.move(move)
                                break
                            elif move.i == from_index and move.j == to_index and move.prom != 0:
                                promoting_moves.append(move)


                        if move_valid and promoting_moves == []:
                            board = bitboards_to_board(position.bitboard, position.turn)
                            board[to_index] = selected_piece
                        
                        elif promoting_moves != []:
                            promoting = True
                            promotion_row, promotion_col = new_pos
                            promotion_color = 'w' if position.turn else 'b'
                            draw_promotion_menu(screen, square_size, promotion_color)
                                
                        elif from_index == 3 and to_index == 1 and Move(0, 2, 0, -1) in valid_moves: # White kingside castling
                            position = position.move(Move(0, 2, 0, -1))
                            board = bitboards_to_board(position.bitboard, position.turn)
                        elif from_index == 3 and to_index == 5 and Move(7, 5, 0, -1) in valid_moves: # White queenside castling
                            position = position.move(Move(7, 5, 0, -1))
                            board = bitboards_to_board(position.bitboard, position.turn)
                        elif from_index == 59 and to_index == 57 and Move(56, 58, 0, -1) in valid_moves: # White queenside castling
                            position = position.move(Move(56, 58, 0, -1))
                            board = bitboards_to_board(position.bitboard, position.turn)
                        elif from_index == 59 and to_index == 61 and Move(63, 60, 0, -1) in valid_moves: # White queenside castling
                            position = position.move(Move(63, 60, 0, -1))
                            board = bitboards_to_board(position.bitboard, position.turn)
                        else:
                            board[from_index] = selected_piece  # Revert to original position

                        dragged_piece = None
                        selected_piece = None

        draw_board(screen, board, dragged_piece, mouse_pos)
        if promoting:
            draw_promotion_menu(screen, square_size, promotion_color)
        pygame.display.flip()

if __name__ == "__main__":
    main()
