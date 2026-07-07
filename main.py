import sys
import pygame

from constants import PIECE_SYMBOLS, UNICODE_PIECES, WHITE
from board import Board
from movegen import generate_pseudo_legal_moves


SQUARE_SIZE = 80
BOARD_SIZE = SQUARE_SIZE * 8

LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)


def square_to_screen(sq):
    '''Bitboard square index -> top-left pixel coords (rank 8 drawn at the top).'''
    rank, file = divmod(sq, 8)
    x = file * SQUARE_SIZE
    y = (7 - rank) * SQUARE_SIZE
    return x, y


def screen_to_square(pos):
    '''Pixel coords -> bitboard square index'''
    x, y = pos
    file = x // SQUARE_SIZE
    rank = 7 - (y // SQUARE_SIZE)
    return rank * 8 + file


def draw_board(screen):
    for rank in range(8):
        for file in range(8):
            color = DARK_SQUARE if (rank + file) & 1 else LIGHT_SQUARE
            rect = pygame.Rect(file * SQUARE_SIZE, (7 - rank) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

            pygame.draw.rect(screen, color, rect)


def draw_pieces(screen, board, font):
    for sq in range(64):
        piece = board.piece_at(sq)
        if piece is None:
            continue

        symbol = PIECE_SYMBOLS[piece]
        glyph = UNICODE_PIECES[symbol]

        text_color = (255, 255, 255) if piece[0] == WHITE else (20, 20, 20)
        text  = font.render(glyph, True, text_color)
        x, y = square_to_screen(sq)
        text_rect = text.get_rect(center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
        screen.blit(text, text_rect)


def highlight_squares(screen, squares):
    for sq in squares:
        x, y = square_to_screen(sq)
        overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

        overlay.fill((*HIGHLIGHT, 140))
        screen.blit(overlay, (x, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    pygame.display.set_caption('BIT-CHESS')
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('segoeuisymbol,dejavusans,arial', 56)

    board = Board()
    selected_sq = None
    legal_targets = []
    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running  = False


            elif event.type == pygame.MOUSEBUTTONDOWN:
                sq = screen_to_square(pygame.mouse.get_pos())
                if selected_sq is None:
                    piece = board.piece_at(sq)

                    if piece and piece[0] == board.side_to_move:
                        selected_sq = sq
                        moves = generate_pseudo_legal_moves(board, board.side_to_move)
                        legal_targets = [m[1] for m in moves if m[0] == sq]

                else:
                    if sq in legal_targets:
                        board.make_move((selected_sq, sq))
                    selected_sq = None
                    legal_targets = []
        
        draw_board(screen)

        if selected_sq is not None:
            highlight_squares(screen, [selected_sq] + legal_targets)
        draw_pieces(screen, board, font)

        pygame.display.flip()
        clock.tick(60)


    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()

