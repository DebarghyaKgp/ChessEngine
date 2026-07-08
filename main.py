import sys
import pygame

from constants import PIECE_SYMBOLS, UNICODE_PIECES, WHITE, BLACK, QUEEN, ROOK, BISHOP, KNIGHT
from board import Board
from movegen import (generate_legal_moves, is_in_check, is_checkmate,
                      is_stalemate, is_insufficient_material)

SQUARE_SIZE = 80
BOARD_SIZE = SQUARE_SIZE * 8

LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)
CHECK_COLOR = (220, 80, 80)
OVERLAY_BG = (0, 0, 0, 170)

PROMOTION_CHOICES = [QUEEN, ROOK, BISHOP, KNIGHT]


def square_to_screen(sq):
    rank, file = divmod(sq, 8)
    x = file * SQUARE_SIZE
    y = (7 - rank) * SQUARE_SIZE
    return x, y


def screen_to_square(pos):
    x, y = pos
    file = x // SQUARE_SIZE
    rank = 7 - (y // SQUARE_SIZE)
    return rank * 8 + file


def draw_board(screen):
    for rank in range(8):
        for file in range(8):
            color = LIGHT_SQUARE if (rank + file) % 2 == 0 else DARK_SQUARE
            rect = pygame.Rect(file * SQUARE_SIZE, (7 - rank) * SQUARE_SIZE,
                                SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)


def draw_pieces(screen, board, font):
    for sq in range(64):
        piece = board.piece_at(sq)
        if piece is None:
            continue
        symbol = PIECE_SYMBOLS[piece]
        glyph = UNICODE_PIECES[symbol]
        text_color = (255, 255, 255) if piece[0] == WHITE else (20, 20, 20)
        text = font.render(glyph, True, text_color)
        x, y = square_to_screen(sq)
        text_rect = text.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
        screen.blit(text, text_rect)


def highlight_squares(screen, squares, color=HIGHLIGHT, alpha=140):
    for sq in squares:
        x, y = square_to_screen(sq)
        overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        overlay.fill((*color, alpha))
        screen.blit(overlay, (x, y))


def draw_promotion_menu(screen, font, color, to_sq):
    """4 stacked squares over the target file, letting the player pick a promotion piece."""
    x, _ = square_to_screen(to_sq)
    rects = []
    for i, piece in enumerate(PROMOTION_CHOICES):
        y = i * SQUARE_SIZE
        rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, (250, 250, 250), rect)
        pygame.draw.rect(screen, (50, 50, 50), rect, 2)
        symbol = PIECE_SYMBOLS[(color, piece)]
        glyph = UNICODE_PIECES[symbol]
        text = font.render(glyph, True, (20, 20, 20))
        screen.blit(text, text.get_rect(center=rect.center))
        rects.append((rect, piece))
    return rects


def draw_game_over_banner(screen, font_big, message):
    overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
    overlay.fill(OVERLAY_BG)
    screen.blit(overlay, (0, 0))
    text = font_big.render(message, True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=(BOARD_SIZE // 2, BOARD_SIZE // 2)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    pygame.display.set_caption("Bitboard Chess")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("segoeuisymbol,dejavusans,arial", 56)
    font_big = pygame.font.SysFont("arial", 40, bold=True)

    board = Board()
    selected_sq = None
    legal_moves_from_selected = []
    pending_promotion = None  # (from_sq, to_sq) awaiting a piece choice
    game_over_message = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and game_over_message is None:
                pos = pygame.mouse.get_pos()

                if pending_promotion is not None:
                    from_sq, to_sq = pending_promotion
                    rects = draw_promotion_menu(screen, font, board.side_to_move, to_sq)
                    for rect, piece in rects:
                        if rect.collidepoint(pos):
                            chosen = next(m for m in legal_moves_from_selected
                                          if m.from_sq == from_sq and m.to_sq == to_sq
                                          and m.promotion == piece)
                            board.make_move(chosen)
                            pending_promotion = None
                            selected_sq = None
                            legal_moves_from_selected = []
                            break
                    continue

                sq = screen_to_square(pos)
                if selected_sq is None:
                    piece = board.piece_at(sq)
                    if piece and piece[0] == board.side_to_move:
                        selected_sq = sq
                        all_legal = generate_legal_moves(board, board.side_to_move)
                        legal_moves_from_selected = [m for m in all_legal if m.from_sq == sq]
                else:
                    candidates = [m for m in legal_moves_from_selected if m.to_sq == sq]
                    if candidates:
                        if len(candidates) > 1:  # multiple promotion options
                            pending_promotion = (selected_sq, sq)
                        else:
                            board.make_move(candidates[0])
                            selected_sq = None
                            legal_moves_from_selected = []
                    else:
                        selected_sq = None
                        legal_moves_from_selected = []

                    if pending_promotion is None and candidates and len(candidates) == 1:
                        # move already applied above; check game end state
                        pass

        # after any move, check for game-ending conditions
        if game_over_message is None and pending_promotion is None:
            if is_checkmate(board, board.side_to_move):
                winner = "White" if board.side_to_move == BLACK else "Black"
                game_over_message = f"Checkmate -- {winner} wins!"
            elif is_stalemate(board, board.side_to_move):
                game_over_message = "Stalemate -- draw!"
            elif is_insufficient_material(board):
                game_over_message = "Draw -- insufficient material!"

        draw_board(screen)
        if selected_sq is not None:
            targets = [m.to_sq for m in legal_moves_from_selected]
            highlight_squares(screen, [selected_sq] + targets)
        if is_in_check(board, board.side_to_move):
            highlight_squares(screen, [board.find_king(board.side_to_move)], color=CHECK_COLOR, alpha=180)
        draw_pieces(screen, board, font)

        if pending_promotion is not None:
            draw_promotion_menu(screen, font, board.side_to_move, pending_promotion[1])

        if game_over_message is not None:
            draw_game_over_banner(screen, font_big, game_over_message)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()