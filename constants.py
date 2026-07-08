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


def opposite_color(color):
    return BLACK if color == WHITE else WHITE
 
# Piece types
PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = range(6)
 
PIECE_SYMBOLS = {
    (WHITE, PAWN): 'P', (WHITE, KNIGHT): 'N', (WHITE, BISHOP): 'B',
    (WHITE, ROOK): 'R', (WHITE, QUEEN): 'Q', (WHITE, KING): 'K',
    (BLACK, PAWN): 'p', (BLACK, KNIGHT): 'n', (BLACK, BISHOP): 'b',
    (BLACK, ROOK): 'r', (BLACK, QUEEN): 'q', (BLACK, KING): 'k',
}
 

# Unicode chess glyphs, used so we don't need external image assets
UNICODE_PIECES = {
    'P': '\u2659', 'N': '\u2658', 'B': '\u2657',
    'R': '\u2656', 'Q': '\u2655', 'K': '\u2654',
    'p': '\u265F', 'n': '\u265E', 'b': '\u265D',
    'r': '\u265C', 'q': '\u265B', 'k': '\u265A',
}
 

# Castling geometry
KING_START = {WHITE: 4, BLACK: 60}                 # e1 / e8
ROOK_KINGSIDE_START = {WHITE: 7, BLACK: 63}         # h1 / h8
ROOK_QUEENSIDE_START = {WHITE: 0, BLACK: 56}        # a1 / a8
 

# Squares that must be empty for the rook to slide through
KINGSIDE_EMPTY = {WHITE: [5, 6], BLACK: [61, 62]}           # f1,g1 / f8,g8
QUEENSIDE_EMPTY = {WHITE: [1, 2, 3], BLACK: [57, 58, 59]}   # b1,c1,d1 / b8,c8,d8
 

# Squares that must NOT be attacked (king's start, transit, and landing square)
KINGSIDE_SAFE = {WHITE: [4, 5, 6], BLACK: [60, 61, 62]}
QUEENSIDE_SAFE = {WHITE: [4, 3, 2], BLACK: [60, 59, 58]}