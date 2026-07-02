from constants import *

def _knight_attacks_from(sq):
    attacks = 0
    r, f = divmod(sq, 8)
    deltas = [(1, 2), (2, 1), (1, -2), (-2, 1), (2, -1), (-1, 2), (-1, -2), (-2, -1)]
    for dr, df in deltas:
        nr, nf = r + dr, f + df
        if 0 <= nr < 8 and 0 < nf < 8:
            attacks |= 1 << (nr * 8 + nf)
    
    return attacks


def _king_attacks_from(sq):
    attacks = 0
    r, f = divmod(sq, 8)
    for dr in (-1, 0, 1):
        for df in (-1, 0, 1):
            if dr == 0 and df == 0:
                continue
        nr, nf = r + dr, f + df
        if 0 <= nr < 8 and 0 <= nf < 8:
            attacks |= (1 << (nr * 8 + nf))
    
    return attacks

# Precomputed at import ... O(1) lookup during move generation
KNIGHT_ATTACKS = [_knight_attacks_from(i) for i in range(64)]
KING_ATTACKS = [_king_attacks_from(i) for i in range(64)]


ROOK_DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]
BISHOP_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

def _sliding_attacks(sq, occupied, directions):
    '''Ray method, ray cast outward in each direction before hitting an occupied square or the edge of the board'''
    attacks = 0
    r0, f0 = divmod(sq, 8)
    for dr, df in directions:
        r, f = r0 + dr, f0 + df

        while 0 <= r < 8 and 0 <= f < 8:
            s = r * 8 + f
            attacks |= 1 << s
            if occupied & (1 << s): # blocked.... ray stops here(capture square included)
                break

            r += dr
            f += df
    
    return attacks


def rook_attacks(sq, occupied):
    return _sliding_attacks(sq, occupied, ROOK_DIRS)

def bishop_attacks(sq, occupied):
    return _sliding_attacks(sq, occupied, BISHOP_DIRS)

def queen_attacks(sq, occupied):
    return rook_attacks(sq, occupied) | bishop_attacks(sq, occupied)


def pawn_capture_targets(sq, color):
    bb = 1 << sq
    if color == WHITE:
        return ((bb & NOT_FILE_A) << 7) | ((bb & NOT_FILE_H) << 9)
    else:
        return ((bb & NOT_FILE_A) >> 9) | ((bb & NOT_FILE_H) >> 7)
    


def generate_pseudo_legal_moves(board, color):
    '''
    Returns a list of (from_sq, to_sq) pseudo_legal moves for 'color'
    Pseudo-legal -> obeys movement/blocking rules, does NOT check whether move leaves mover's own king in check
    '''
    
    moves = []
    own = board.occupied_by(color)
    enemy = board.occupied_by(BLACK if color == WHITE else WHITE)
    occ = own | enemy

    for (col, piece), bb in board.bitboards.items():
        if col != color or bb == 0:
            continue

        bb_copy = bb
        while bb_copy:
            sq = (bb_copy & -bb_copy).bit_length() - 1  # index of lowest set bit
            
            bb_copy &= bb_copy - 1  # clear lowest set bit

            if piece == KNIGHT:
                targets = KNIGHT_ATTACKS[sq] & ~own

            elif piece == KING:
                targets = KING_ATTACKS[sq] & ~own
            
            elif piece == ROOK:
                targets = rook_attacks(sq, occ) & ~own
            
            elif piece == QUEEN:
                targets = rook_attacks(sq, occ) & ~own
            
            elif piece == BISHOP:
                targets = bishop_attacks(sq, occ) & ~ own

            elif piece == PAWN:
                targets = 0
                forward = 8 if color == WHITE else -8
                single = sq + forward
                if 0 <= single < 64 and not(occ & (1 << single)):
                    targets |= 1 << single
                    start_rank = 1 if color == WHITE else 6
                    if sq // 8 == start_rank:
                        double = sq + 2 * forward
                        if not (occ & (1 << double)):
                            targets |= (1 << double)
                
                targets |= pawn_capture_targets(sq, color) & enemy
            
            else:
                targets = 0
            
            t_copy = targets
            while t_copy:
                to_sq = (t_copy & -t_copy).bit_length() - 1
                t_copy &= t_copy - 1
                moves.append((sq, to_sq))

       
    return moves




