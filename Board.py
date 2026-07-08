''' 
For Visualization Purposes:
Hexadecimal to Binary

|Hex|  Bin | |Hex| Bin 
| 0 | 0000 | | 8 | 1000 
| 1 | 0001 | | 9 | 1001 
| 2 | 0010 | | A | 1010 
| 3 | 0011 | | B | 1011 
| 4 | 0100 | | C | 1100 
| 5 | 0101 | | D | 1101 
| 6 | 0110 | | E | 1110 
| 7 | 0111 | | F | 1111

'''
from constants import *
from moves import Move

START_POSITION = {
    (WHITE, PAWN):   0x000000000000FF00,
    (WHITE, ROOK):   0x0000000000000081,
    (WHITE, KNIGHT): 0x0000000000000042,
    (WHITE, BISHOP): 0x0000000000000024,
    (WHITE, QUEEN):  0x0000000000000008,
    (WHITE, KING):   0x0000000000000010,
    (BLACK, PAWN):   0x00FF000000000000,
    (BLACK, ROOK):   0x8100000000000000,
    (BLACK, KNIGHT): 0x4200000000000000,
    (BLACK, BISHOP): 0x2400000000000000,
    (BLACK, QUEEN):  0x0800000000000000,
    (BLACK, KING):   0x1000000000000000,
}


class Board:
    def __init__(self):
        self.bitboards = dict(START_POSITION)
        self.side_to_move = WHITE
        # 'K'/'Q' = white king-side/queen-side, 'k'/'q' = black
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant_square = None  # square a pawn could capture into via en passant, right now

    def copy(self):
        """Cheap snapshot used to test 'what if I make this move' without mutating the real board."""
        new = Board.__new__(Board)
        new.bitboards = dict(self.bitboards)
        new.side_to_move = self.side_to_move
        new.castling_rights = dict(self.castling_rights)
        new.en_passant_square = self.en_passant_square
        return new

    def occupied(self):
        occ = 0
        for bb in self.bitboards.values():
            occ |= bb
        return occ

    def occupied_by(self, color):
        occ = 0
        for (col, _piece), bb in self.bitboards.items():
            if col == color:
                occ |= bb
        return occ

    def piece_at(self, square):
        mask = 1 << square
        for (color, piece), bb in self.bitboards.items():
            if bb & mask:
                return color, piece
        return None

    def find_king(self, color):
        bb = self.bitboards[(color, KING)]
        return (bb & -bb).bit_length() - 1

    def make_move(self, move: Move):
        """Apply a Move (see moves.py). No legality checking here -- that's movegen's job."""
        color, piece = self.piece_at(move.from_sq)
        opp = opposite_color(color)

        if move.is_en_passant:
            # the captured pawn is NOT on to_sq -- it's the square behind it
            captured_sq = move.to_sq - 8 if color == WHITE else move.to_sq + 8
            self.bitboards[(opp, PAWN)] &= ~(1 << captured_sq)
        else:
            captured = self.piece_at(move.to_sq)
            if captured:
                cap_color, cap_piece = captured
                self.bitboards[(cap_color, cap_piece)] &= ~(1 << move.to_sq)

        # move the piece off its origin square
        self.bitboards[(color, piece)] &= ~(1 << move.from_sq)
        if move.promotion:
            # pawn becomes a different piece type on arrival
            self.bitboards[(color, move.promotion)] |= (1 << move.to_sq)
        else:
            self.bitboards[(color, piece)] |= (1 << move.to_sq)

        # castling also drags the rook to its new square
        if move.is_castle:
            if move.to_sq == 6:      # white king-side (e1-g1)
                self.bitboards[(WHITE, ROOK)] &= ~(1 << 7)
                self.bitboards[(WHITE, ROOK)] |= (1 << 5)
            elif move.to_sq == 2:    # white queen-side (e1-c1)
                self.bitboards[(WHITE, ROOK)] &= ~(1 << 0)
                self.bitboards[(WHITE, ROOK)] |= (1 << 3)
            elif move.to_sq == 62:   # black king-side (e8-g8)
                self.bitboards[(BLACK, ROOK)] &= ~(1 << 63)
                self.bitboards[(BLACK, ROOK)] |= (1 << 61)
            elif move.to_sq == 58:   # black queen-side (e8-c8)
                self.bitboards[(BLACK, ROOK)] &= ~(1 << 56)
                self.bitboards[(BLACK, ROOK)] |= (1 << 59)

        # castling rights: lost permanently once king or a rook moves (or a rook is captured)
        if piece == KING:
            if color == WHITE:
                self.castling_rights['K'] = False
                self.castling_rights['Q'] = False
            else:
                self.castling_rights['k'] = False
                self.castling_rights['q'] = False
        for sq, key in ((0, 'Q'), (7, 'K'), (56, 'q'), (63, 'k')):
            if move.from_sq == sq or move.to_sq == sq:
                self.castling_rights[key] = False

        # en passant target: only alive for the one move right after a double pawn push
        if piece == PAWN and abs(move.to_sq - move.from_sq) == 16:
            self.en_passant_square = (move.from_sq + move.to_sq) // 2
        else:
            self.en_passant_square = None

        self.side_to_move = opp
        return True

    def print_board(self):
        for rank in range(7, -1, -1):
            row = ""
            for file in range(8):
                sq = rank * 8 + file
                p = self.piece_at(sq)
                row += (PIECE_SYMBOLS[p] if p else ".") + " "
            print(row)
        print()


