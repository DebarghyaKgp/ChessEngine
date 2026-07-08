from constants import *
from moves import Move


def _knight_attacks_from(sq):
    attacks = 0
    r, f = divmod(sq, 8)
    deltas = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
    for dr, df in deltas:
        nr, nf = r + dr, f + df
        if 0 <= nr < 8 and 0 <= nf < 8:
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
                attacks |= 1 << (nr * 8 + nf)
    return attacks


KNIGHT_ATTACKS = [_knight_attacks_from(sq) for sq in range(64)]
KING_ATTACKS = [_king_attacks_from(sq) for sq in range(64)]

ROOK_DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
BISHOP_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def _sliding_attacks(sq, occupied, directions):
    attacks = 0
    r0, f0 = divmod(sq, 8)
    for dr, df in directions:
        r, f = r0 + dr, f0 + df
        while 0 <= r < 8 and 0 <= f < 8:
            s = r * 8 + f
            attacks |= 1 << s
            if occupied & (1 << s):
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


PROMOTION_PIECES = (QUEEN, ROOK, BISHOP, KNIGHT)


def generate_pseudo_legal_moves(board, color):
    """Obeys movement/blocking rules. Does NOT filter out moves that leave your own king in check."""
    moves = []
    own = board.occupied_by(color)
    enemy = board.occupied_by(opposite_color(color))
    occ = own | enemy
    last_rank = 7 if color == WHITE else 0

    for (c, piece), bb in board.bitboards.items():
        if c != color or bb == 0:
            continue
        bb_copy = bb
        while bb_copy:
            sq = (bb_copy & -bb_copy).bit_length() - 1
            bb_copy &= bb_copy - 1

            if piece == KNIGHT:
                targets = KNIGHT_ATTACKS[sq] & ~own
            elif piece == KING:
                targets = KING_ATTACKS[sq] & ~own
            elif piece == ROOK:
                targets = rook_attacks(sq, occ) & ~own
            elif piece == BISHOP:
                targets = bishop_attacks(sq, occ) & ~own
            elif piece == QUEEN:
                targets = queen_attacks(sq, occ) & ~own
            elif piece == PAWN:
                forward = 8 if color == WHITE else -8
                single = sq + forward
                push_targets = 0
                if 0 <= single < 64 and not (occ & (1 << single)):
                    push_targets |= (1 << single)
                    start_rank = 1 if color == WHITE else 6
                    if sq // 8 == start_rank:
                        double = sq + 2 * forward
                        if not (occ & (1 << double)):
                            push_targets |= (1 << double)

                capture_mask = pawn_capture_targets(sq, color)
                normal_captures = capture_mask & enemy
                ep_capture = 0
                if board.en_passant_square is not None:
                    ep_capture = capture_mask & (1 << board.en_passant_square)

                def _emit_pawn_targets(target_bb, is_ep=False):
                    t_copy = target_bb
                    while t_copy:
                        to_sq = (t_copy & -t_copy).bit_length() - 1
                        t_copy &= t_copy - 1
                        if is_ep:
                            moves.append(Move(sq, to_sq, None, False, True))
                        elif to_sq // 8 == last_rank:
                            for promo in PROMOTION_PIECES:
                                moves.append(Move(sq, to_sq, promo, False, False))
                        else:
                            moves.append(Move(sq, to_sq, None, False, False))

                _emit_pawn_targets(push_targets)
                _emit_pawn_targets(normal_captures)
                _emit_pawn_targets(ep_capture, is_ep=True)
                continue  # pawns fully handled -- skip the generic emission below
            else:
                targets = 0

            t_copy = targets
            while t_copy:
                to_sq = (t_copy & -t_copy).bit_length() - 1
                t_copy &= t_copy - 1
                moves.append(Move(sq, to_sq, None, False, False))

    return moves


def is_square_attacked(board, square, by_color):
    """Is `square` attacked by any `by_color` piece? Runs each attack pattern in reverse from `square`."""
    occ = board.occupied()
    opp_of_by = opposite_color(by_color)

    if pawn_capture_targets(square, opp_of_by) & board.bitboards[(by_color, PAWN)]:
        return True
    if KNIGHT_ATTACKS[square] & board.bitboards[(by_color, KNIGHT)]:
        return True
    if KING_ATTACKS[square] & board.bitboards[(by_color, KING)]:
        return True
    if rook_attacks(square, occ) & (board.bitboards[(by_color, ROOK)] | board.bitboards[(by_color, QUEEN)]):
        return True
    if bishop_attacks(square, occ) & (board.bitboards[(by_color, BISHOP)] | board.bitboards[(by_color, QUEEN)]):
        return True
    return False


def is_in_check(board, color):
    king_sq = board.find_king(color)
    return is_square_attacked(board, king_sq, opposite_color(color))


def generate_castling_moves(board, color):
    moves = []
    occ = board.occupied()
    opp = opposite_color(color)

    if color == WHITE:
        if board.castling_rights['K'] and (board.bitboards[(WHITE, ROOK)] & (1 << 7)):
            if not (occ & ((1 << 5) | (1 << 6))):
                if not any(is_square_attacked(board, sq, opp) for sq in (4, 5, 6)):
                    moves.append(Move(4, 6, None, True, False))
        if board.castling_rights['Q'] and (board.bitboards[(WHITE, ROOK)] & (1 << 0)):
            if not (occ & ((1 << 1) | (1 << 2) | (1 << 3))):
                if not any(is_square_attacked(board, sq, opp) for sq in (4, 3, 2)):
                    moves.append(Move(4, 2, None, True, False))
    else:
        if board.castling_rights['k'] and (board.bitboards[(BLACK, ROOK)] & (1 << 63)):
            if not (occ & ((1 << 61) | (1 << 62))):
                if not any(is_square_attacked(board, sq, opp) for sq in (60, 61, 62)):
                    moves.append(Move(60, 62, None, True, False))
        if board.castling_rights['q'] and (board.bitboards[(BLACK, ROOK)] & (1 << 56)):
            if not (occ & ((1 << 57) | (1 << 58) | (1 << 59))):
                if not any(is_square_attacked(board, sq, opp) for sq in (60, 59, 58)):
                    moves.append(Move(60, 58, None, True, False))
    return moves


def generate_legal_moves(board, color):
    """Pseudo-legal moves + castling, filtered to exclude any that leave your own king in check."""
    candidates = generate_pseudo_legal_moves(board, color) + generate_castling_moves(board, color)
    legal = []
    for move in candidates:
        trial = board.copy()
        trial.make_move(move)
        if not is_in_check(trial, color):
            legal.append(move)
    return legal


def is_checkmate(board, color):
    return is_in_check(board, color) and len(generate_legal_moves(board, color)) == 0


def is_stalemate(board, color):
    return (not is_in_check(board, color)) and len(generate_legal_moves(board, color)) == 0


LIGHT_SQUARES = 0x55AA55AA55AA55AA  # a1 is dark square

def is_insufficient_material(board):
    """
    True if neither side has enough material to force checkmate:
      K vs K | K+N vs K | K+B vs K | K+B vs K+B with same-colored bishops.
    Any pawn, rook, or queen on the board means mate is still possible -> False.
    """
    if (board.bitboards[(WHITE, PAWN)] or board.bitboards[(BLACK, PAWN)]
            or board.bitboards[(WHITE, ROOK)] or board.bitboards[(BLACK, ROOK)]
            or board.bitboards[(WHITE, QUEEN)] or board.bitboards[(BLACK, QUEEN)]):
        return False
 
    white_knights = bin(board.bitboards[(WHITE, KNIGHT)]).count('1')
    black_knights = bin(board.bitboards[(BLACK, KNIGHT)]).count('1')
    white_bishops_bb = board.bitboards[(WHITE, BISHOP)]
    black_bishops_bb = board.bitboards[(BLACK, BISHOP)]
    white_bishops = bin(white_bishops_bb).count('1')
    black_bishops = bin(black_bishops_bb).count('1')
 
    white_minor = white_knights + white_bishops
    black_minor = black_knights + black_bishops
 
    # K vs K
    if white_minor == 0 and black_minor == 0:
        return True
 
    # K+one minor vs K
    if (white_minor == 1 and black_minor == 0) or (white_minor == 0 and black_minor == 1):
        return True
 
    # K+B vs K+B, same-colored bishops (no knights involved)
    if white_minor == 1 and black_minor == 1 and white_knights == 0 and black_knights == 0:
        white_on_light = bool(white_bishops_bb & LIGHT_SQUARES)
        black_on_light = bool(black_bishops_bb & LIGHT_SQUARES)
        if white_on_light == black_on_light:
            return True
 
    return False