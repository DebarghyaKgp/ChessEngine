"""
Bitboard chess constants.
 
Squares are numbered 0-63:
  a1 = 0, b1 = 1, ... h1 = 7,
  a2 = 8, ... h8 = 63
(rank-major, "LERF" mapping — same as most bitboard engines.)

LERF -> Little Endian Rank File
"""

SQUARE_NAMES = [f'{file}{rank}' for rank in range(1, 9) for file in 'abcdefgh']

# print(SQUARE_NAMES)

FILE_A =     0x0101010101010101
FILE_H = FILE_A << 7

RANK_1 =     0x00000000000000FF
RANK_8 = RANK_1 << 56

FULL_BOARD = 0xFFFFFFFFFFFFFFFF

NOT_FILE_A = ~FILE_A & FULL_BOARD
NOT_FILE_H = ~FILE_H & FULL_BOARD

WHITE, BLACK = 0, 1

PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = range(6) 

PIECE_SYMBOLS = {
    (WHITE, PAWN):   'P', (BLACK, PAWN): 'p',
    (WHITE, ROOK):   'R', (BLACK, ROOK): 'r',
    (WHITE, KNIGHT): 'N', (BLACK, KNIGHT): 'n',
    (WHITE, BISHOP): 'B', (BLACK, BISHOP): 'b',
    (WHITE, QUEEN):  'Q', (BLACK, QUEEN): 'q',
    (WHITE, KING):   'K', (BLACK, KING): 'k'
}


# Using unicode glyphs, so that no external sprites need not be used
UNICODE_PIECES = {
    'P': '\u2659', 'p':'\u265F',
    'R': '\u2658', 'r':'\u265E',
    'N': '\u2657', 'n':'\u265D',
    'B': '\u2656', 'b':'\u265C',
    'Q': '\u2655', 'q':'\u265B',
    'K': '\u2654', 'k':'\u265A'
}

