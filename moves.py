from collections import namedtuple
 
# promotion: None, or one of QUEEN/ROOK/BISHOP/KNIGHT (piece-type constants from constants.py)
Move = namedtuple('Move', ['from_sq', 'to_sq', 'promotion', 'is_castle', 'is_en_passant'])
Move.__new__.__defaults__ = (None, False, False)  # promotion, is_castle, is_en_passant all optional