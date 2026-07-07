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

class Board:
    def __init__(self):
        self.bitboards = {
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
            (BLACK, KING):   0x1000000000000000
        }
        
        self.side_to_move = WHITE
    

    def occupied(self):
        '''All squares occupied by any piece'''
        occ = 0
        for bb in self.bitboards.values():
            occ |= bb
        
        return occ

    def occupied_by(self, color):
        '''All squares occupied by a given color'''
        occ = 0
        for (col, type), bb in self.bitboards.items():
            if col == color:
                occ |= bb
        
        return occ
    
    def piece_at(self, square):
        '''Returns (color, piece_type) at a given square, or None of empty'''

        mask = 1 << square
        for (color, piece), bb in self.bitboards.items():
            if bb & mask:
                return color, piece
        return None


    def make_move(self, move):
        '''Apply a move given as (from, to). No legality checks here.'''
        
        from_sq, to_sq = move
        moving = self.piece_at(from_sq)
        if not moving:
            return False
        color, piece = moving

        # moving to capture
        captured = self.piece_at(to_sq)
        if captured:
            cap_color, cap_piece = captured
            self.bitboards[(cap_color, cap_piece)] &= ~ (1 << to_sq)

        self.bitboards[(color, piece)] &= ~(1 << from_sq)
        self.bitboards[(color, piece)] |= (1 << to_sq)

        self.side_to_move = BLACK if self.side_to_move == WHITE else WHITE
        return True



    def print_board(self) -> None:
        '''for debugging, prints rank 8 -> rank 1'''
        for rank in range(7, -1, -1):
            row = ''
            for file in range(8):
                sq = rank * 8 + file
                p = self.piece_at(sq)
                row += (PIECE_SYMBOLS[p] if p else '.') + ' '
            print(row)
        print()


