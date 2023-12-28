import pygame
import sys
import time
import argparse


from BitPosition import Move, BitPosition, Engine, evaluation_function_black, evaluation_function_white
from utils import board_to_bitboards, bitboards_to_board

def parse_arguments():
    parser = argparse.ArgumentParser(description="Play Chess")
    parser.add_argument("--mode", choices=['engine', 'self'], required=True,
                        help="Choose to play against the engine or yourself")
    parser.add_argument("--side", choices=['white', 'black'], required=True,
                        help="Choose your side")
    return parser.parse_args()


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
            piece = board[(7-row) * 8 + col]
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
    row = 7 - y // square_size
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

def play_and_undo_moves(position, depth, screen, square_size, pieces_images, board, promoting, promotion_color):
    if depth == 0:
        return

    if not position.is_check():
        valid_moves = list(position.capture_moves()) + list(position.non_capture_moves())
    else:
        valid_moves = list(position.in_check_captures()) + list(position.in_check_moves())

    for move in valid_moves:
        position.move(move)
        updated_board = bitboards_to_board(position.bitboard)
        draw_board(screen, updated_board, None, (0, 0))
        pygame.display.flip()
        time.sleep(1)  # Wait for 1 second

        # Recursive call to the next depth
        play_and_undo_moves(position, depth - 1, screen, square_size, pieces_images, updated_board, promoting, promotion_color)

        position.unmake_move(move)
        draw_board(screen, board, None, (0, 0))
        pygame.display.flip()

move_history = []

def main():
    args = parse_arguments()
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

    pieces_images = load_pieces_images(square_size)
    board = [
    'wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR',
    'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP',
    '0', '0', '0', '0', '0', '0', '0', '0',
    '0', '0', '0', '0', '0', '0', '0', '0',
    '0', '0', '0', '0', '0', '0', '0', '0',
    '0', '0', '0', '0', '0', '0', '0', '0',
    'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP',
    'bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'
]
    bitboards_array = board_to_bitboards(board)
    position = BitPosition(bitboards_array, turn = True)

    while True:
        if args.mode == 'engine':
            player_is_white = args.side == 'white'
            if player_is_white:
                engine = Engine(evaluation_function_black)
                engine_turn = False
            else:
                engine = Engine(evaluation_function_white)
                engine_turn = True

            mouse_pos = pygame.mouse.get_pos()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.MOUSEBUTTONDOWN: # Left click down
                    selected_pos = get_square_at_pos(mouse_pos, square_size)
                    selected_piece = board[selected_pos[0] * 8 + selected_pos[1]]
                    if selected_piece != '0':
                        dragged_piece = (pieces_images[selected_piece], pieces_images[selected_piece].get_rect(topleft=mouse_pos))
                        board[selected_pos[0] * 8 + selected_pos[1]] = '0'
                elif e.type == pygame.MOUSEBUTTONUP: # Left click up
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
                                    position.move(move)
                                    move_history.append(move)
                                    board = bitboards_to_board(position.bitboard)
                                    board[to_index] = promotion_color + choice
                                    break

                            promoting = False
                            promoting_moves = []
                            engine_turn = True
                    else:
                        if dragged_piece:
                            new_pos = get_square_at_pos(mouse_pos, square_size)
                            from_index = selected_pos[0] * 8 + selected_pos[1]
                            to_index = new_pos[0] * 8 + new_pos[1]
                            if not position.is_check():
                                valid_moves = list(position.capture_moves()) + list(position.non_capture_moves())
                            else:
                                valid_moves = list(position.in_check_captures()) + list(position.in_check_moves())
                            move_valid = False
                            promoting_moves = []

                            for move in valid_moves:
                                if move.i == from_index and move.j == to_index and move.prom == 0:
                                    move_valid = True
                                    position.move(move)
                                    move_history.append(move)
                                    engine_turn = True
                                    break
                                elif move.i == from_index and move.j == to_index and move.prom != 0:
                                    promoting_moves.append(move)


                            if move_valid and promoting_moves == []:
                                board = bitboards_to_board(position.bitboard)
                                board[to_index] = selected_piece
                            
                            elif promoting_moves != []:
                                promoting = True
                                promotion_row, promotion_col = new_pos
                                promotion_color = 'w' if position.turn else 'b'
                                draw_promotion_menu(screen, square_size, promotion_color)
                                    
                            elif from_index == 4 and to_index == 6 and Move(7, 5, 0, -1) in valid_moves: # White kingside castling
                                position.move(Move(7, 5, 0, -1))
                                move_history.append(Move(7, 5, 0, -1))
                                board = bitboards_to_board(position.bitboard)
                                engine_turn = True
                            elif from_index == 4 and to_index == 2 and Move(0, 3, 0, -1) in valid_moves: # White queenside castling
                                position.move(Move(0, 3, 0, -1))
                                move_history.append(Move(0, 3, 0, -1))
                                board = bitboards_to_board(position.bitboard)
                                engine_turn = True
                            elif from_index == 60 and to_index == 62 and Move(63, 61, 0, -1) in valid_moves: # Black kingside castling
                                position.move(Move(63, 61, 0, -1))
                                move_history.append(Move(63, 61, 0, -1))
                                board = bitboards_to_board(position.bitboard)
                                engine_turn = True
                            elif from_index == 60 and to_index == 58 and Move(56, 59, 0, -1) in valid_moves: # Black queenside castling
                                position.move(Move(56, 59, 0, -1))
                                move_history.append(Move(56, 59, 0, -1))
                                board = bitboards_to_board(position.bitboard)
                                engine_turn = True
                            else:
                                board[from_index] = selected_piece  # Revert to original position

                            dragged_piece = None
                            selected_piece = None
                if  engine_turn:
                    engine_move = engine.Search(position, 5)[4]  # Replace 'engine' with your engine's variable
                    position.move(engine_move)
                    move_history.append(engine_move)
                    board = bitboards_to_board(position.bitboard)
                    engine_turn = False  # Switch turns

                
        else:
            mouse_pos = pygame.mouse.get_pos()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif e.type == pygame.MOUSEBUTTONDOWN: # Left click down
                    print('checks:', position.current_checks)
                    print('pins:', position.current_pins)
                    selected_pos = get_square_at_pos(mouse_pos, square_size)
                    selected_piece = board[selected_pos[0] * 8 + selected_pos[1]]
                    if selected_piece != '0':
                        dragged_piece = (pieces_images[selected_piece], pieces_images[selected_piece].get_rect(topleft=mouse_pos))
                        board[selected_pos[0] * 8 + selected_pos[1]] = '0'
                elif e.type == pygame.MOUSEBUTTONUP: # Left click up
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
                                    position.move(move)
                                    move_history.append(move)
                                    board = bitboards_to_board(position.bitboard)
                                    board[to_index] = promotion_color + choice
                                    break

                            promoting = False
                            promoting_moves = []
                    else:
                        if dragged_piece:
                            new_pos = get_square_at_pos(mouse_pos, square_size)
                            from_index = selected_pos[0] * 8 + selected_pos[1]
                            to_index = new_pos[0] * 8 + new_pos[1]
                            print('from index:', from_index)
                            print('to index:', to_index)
                            if not position.is_check():
                                valid_moves = list(position.capture_moves()) + list(position.non_capture_moves())
                            else:
                                valid_moves = list(position.in_check_captures()) + list(position.in_check_moves())
                            move_valid = False
                            promoting_moves = []

                            for move in valid_moves:
                                if move.i == from_index and move.j == to_index and move.prom == 0:
                                    move_valid = True
                                    position.move(move)
                                    move_history.append(move)
                                    break
                                elif move.i == from_index and move.j == to_index and move.prom != 0:
                                    promoting_moves.append(move)


                            if move_valid and promoting_moves == []:
                                board = bitboards_to_board(position.bitboard)
                                board[to_index] = selected_piece
                            
                            elif promoting_moves != []:
                                promoting = True
                                promotion_row, promotion_col = new_pos
                                promotion_color = 'w' if position.turn else 'b'
                                draw_promotion_menu(screen, square_size, promotion_color)
                                    
                            elif from_index == 4 and to_index == 6 and Move(7, 5, 0, -1) in valid_moves: # White kingside castling
                                position.move(Move(7, 5, 0, -1))
                                move_history.append(Move(7, 5, 0, -1))
                                board = bitboards_to_board(position.bitboard)
                            elif from_index == 4 and to_index == 2 and Move(0, 3, 0, -1) in valid_moves: # White queenside castling
                                position.move(Move(0, 3, 0, -1))
                                move_history.append(Move(0, 3, 0, -1))
                                board = bitboards_to_board(position.bitboard)
                            elif from_index == 60 and to_index == 62 and Move(63, 61, 0, -1) in valid_moves: # Black kingside castling
                                position.move(Move(63, 61, 0, -1))
                                move_history.append(Move(63, 61, 0, -1))
                                board = bitboards_to_board(position.bitboard)
                            elif from_index == 60 and to_index == 58 and Move(56, 59, 0, -1) in valid_moves: # Black queenside castling
                                position.move(Move(56, 59, 0, -1))
                                move_history.append(Move(56, 59, 0, -1))
                                board = bitboards_to_board(position.bitboard)
                            else:
                                board[from_index] = selected_piece  # Revert to original position

                            dragged_piece = None
                            selected_piece = None

                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT: # Pressing left key to undo last move
                        if move_history:  # Check if there are moves to undo
                            last_move = move_history.pop()  # Get the last move
                            position.unmake_move(last_move)  # Undo the last move
                            board = bitboards_to_board(position.bitboard)  # Update board display

                    elif e.key == pygame.K_SPACE:  # Press SPACE to start the auto-play and undo
                        play_and_undo_moves(position, 1, screen, square_size, pieces_images, board, promoting, promotion_color)  # Depth is set to 2 here


        draw_board(screen, board, dragged_piece, mouse_pos)
        if promoting:
            draw_promotion_menu(screen, square_size, promotion_color)
        pygame.display.flip()

if __name__ == "__main__":
    main()
