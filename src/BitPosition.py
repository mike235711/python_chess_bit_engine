import json
import copy
import numpy as np
import random

###################################################
# BitBoards for Crawlers (Pawns, Knights and King)
###################################################

# For crawlers we can easily compute possible moves using the bit encoded position and a 
# precomputed table of the positions in which it may move from each square. Here it is not 
# needed to use symmetries, since there is not too many bits to store. For sliders it is different.

########################################################################
# Magic BitBoards and Magic Numbers for Sliders (Rooks, Bishops, Queens)
########################################################################

# Magic BitBoards are a clever method that uses precomputed tables of where pieces may move from a certain square. 
# Precomputed tables contain for each piece a number which represents the moves it can make taking into account the
# blocking pieces, each of the pairs piece, square has a magic number which when multplying in some way gives a
# new number, this number is the index. Which corresponds to the index of the array of possible moves the piece
# can make taking into account the blocking pieces.
# 
# One doesn't need to store the configurations when there is a piece at the edge of the board, since this doesn't 
# block further the path, as there are no further squares along that path. This reduces greatly the amount of 
# configurations stored. 
# 
# To find more about magic numbers see: Coding Adventure: Making a Better Chess Bot minute 28.30-39.00.
#
# My own idea is to exploit the symmetries so that for each piece we only need to store 16 bitboards instead of 
# 64. This makes finding the magic number easier, maybe even there's a smart way of ordering the bits for each square
# without using magic numbers.

###################################
# Zobrist Hashing Inizialization
###################################

random_numbers = set()
random.seed(96620)
while len(random_numbers) < 801:
    random_numbers.add(random.randint(1, 2**64 - 1))
random_numbers = list(random_numbers)

white_pawn_zobrist_numbers = np.array(random_numbers[:64])
white_knight_zobrist_numbers = np.array(random_numbers[64:2*64])
white_bishop_zobrist_numbers = np.array(random_numbers[2*64:3*64])
white_rook_zobrist_numbers = np.array(random_numbers[3*64:4*64])
white_queen_zobrist_numbers = np.array(random_numbers[4*64:5*64])
white_king_zobrist_numbers = np.array(random_numbers[5*64:6*64])
black_pawn_zobrist_numbers = np.array(random_numbers[6*64:7*64])
black_knight_zobrist_numbers = np.array(random_numbers[7*64:8*64])
black_bishop_zobrist_numbers = np.array(random_numbers[8*64:9*64])
black_rook_zobrist_numbers = np.array(random_numbers[9*64:10*64])
black_queen_zobrist_numbers = np.array(random_numbers[10*64:11*64])
black_king_zobrist_numbers = np.array(random_numbers[11*64:12*64])

black_to_move_zobrist_number = random_numbers[12*64]

castling_rights_zobrist_numbers = np.array(random_numbers[((12*64)+1):((12*64)+17)])

passant_squares_zobrist_numbers = {-1: 0, 
                     16 : random_numbers[(12*64)+17], 17 : random_numbers[(12*64)+18], 18 : random_numbers[(12*64)+19], 19 : random_numbers[(12*64)+20], 20 : random_numbers[(12*64)+21], 21 : random_numbers[(12*64)+22], 22 : random_numbers[(12*64)+23], 23: random_numbers[(12*64)+24], 
                     40 : random_numbers[(12*64)+25], 41 : random_numbers[(12*64)+26], 42 : random_numbers[(12*64)+27], 43 : random_numbers[(12*64)+28], 44 : random_numbers[(12*64)+29], 45 : random_numbers[(12*64)+30], 46 : random_numbers[(12*64)+31], 47 : random_numbers[(12*64)+32]}

zobrist_numbers_pieces = (white_pawn_zobrist_numbers, white_knight_zobrist_numbers, white_bishop_zobrist_numbers, white_rook_zobrist_numbers, 
                         white_queen_zobrist_numbers, white_king_zobrist_numbers, black_pawn_zobrist_numbers, black_king_zobrist_numbers, 
                         black_bishop_zobrist_numbers, black_rook_zobrist_numbers, black_queen_zobrist_numbers, black_king_zobrist_numbers)

####################################
# Pre-computed crawler tables 
####################################


# Precomputed move tables
knight_moves = (132096, 329728, 659712, 1319424, 2638848, 5277696, 10489856, 4202496, 33816580, 84410376, 168886289, 337772578, 675545156, 1351090312, 2685403152, 1075839008, 8657044482, 21609056261, 43234889994, 86469779988, 172939559976, 345879119952, 687463207072, 275414786112, 2216203387392, 5531918402816, 11068131838464, 22136263676928, 44272527353856, 88545054707712, 175990581010432, 70506185244672, 567348067172352, 1416171111120896, 2833441750646784, 5666883501293568, 11333767002587136, 22667534005174272, 45053588738670592, 18049583422636032, 145241105196122112, 362539804446949376, 725361088165576704, 1450722176331153408, 2901444352662306816, 5802888705324613632, 11533718717099671552, 4620693356194824192, 288234782788157440, 576469569871282176, 1224997833292120064, 2449995666584240128, 4899991333168480256, 9799982666336960512, 1152939783987658752, 2305878468463689728, 1128098930098176, 2257297371824128, 4796069720358912, 9592139440717824, 19184278881435648, 38368557762871296, 4679521487814656, 9077567998918656)
king_moves = (770, 1797, 3594, 7188, 14376, 28752, 57504, 49216, 197123, 460039, 920078, 1840156, 3680312, 7360624, 14721248, 12599488, 50463488, 117769984, 235539968, 471079936, 942159872, 1884319744, 3768639488, 3225468928, 12918652928, 30149115904, 60298231808, 120596463616, 241192927232, 482385854464, 964771708928, 825720045568, 3307175149568, 7718173671424, 15436347342848, 30872694685696, 61745389371392, 123490778742784, 246981557485568, 211384331665408, 846636838289408, 1975852459884544, 3951704919769088, 7903409839538176, 15806819679076352, 31613639358152704, 63227278716305408, 54114388906344448, 216739030602088448, 505818229730443264, 1011636459460886528, 2023272918921773056, 4046545837843546112, 8093091675687092224, 16186183351374184448, 13853283560024178688, 144959613005987840, 362258295026614272, 724516590053228544, 1449033180106457088, 2898066360212914176, 5796132720425828352, 11592265440851656704, 4665729213955833856)
white_pawn_moves = (0, 0, 0, 0, 0, 0, 0, 0, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648, 4294967296, 8589934592, 17179869184, 34359738368, 68719476736, 137438953472, 274877906944, 549755813888, 1099511627776, 2199023255552, 4398046511104, 8796093022208, 17592186044416, 35184372088832, 70368744177664, 140737488355328, 281474976710656, 562949953421312, 1125899906842624, 2251799813685248, 4503599627370496, 9007199254740992, 18014398509481984, 36028797018963968, 72057594037927936, 144115188075855872, 288230376151711744, 576460752303423488, 1152921504606846976, 2305843009213693952, 4611686018427387904, 9223372036854775808, 0, 0, 0, 0, 0, 0, 0, 0)
white_pawn_attacks = (512, 1280, 2560, 5120, 10240, 20480, 40960, 16384, 131072, 327680, 655360, 1310720, 2621440, 5242880, 10485760, 4194304, 33554432, 83886080, 167772160, 335544320, 671088640, 1342177280, 2684354560, 1073741824, 8589934592, 21474836480, 42949672960, 85899345920, 171798691840, 343597383680, 687194767360, 274877906944, 2199023255552, 5497558138880, 10995116277760, 21990232555520, 43980465111040, 87960930222080, 175921860444160, 70368744177664, 562949953421312, 1407374883553280, 2814749767106560, 5629499534213120, 11258999068426240, 22517998136852480, 45035996273704960, 18014398509481984, 144115188075855872, 360287970189639680, 720575940379279360, 1441151880758558720, 2882303761517117440, 5764607523034234880, 11529215046068469760, 4611686018427387904, 0, 0, 0, 0, 0, 0, 0, 0)
black_pawn_moves = (0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648, 4294967296, 8589934592, 17179869184, 34359738368, 68719476736, 137438953472, 274877906944, 549755813888, 1099511627776, 2199023255552, 4398046511104, 8796093022208, 17592186044416, 35184372088832, 70368744177664, 140737488355328, 0, 0, 0, 0, 0, 0, 0, 0)
black_pawn_attacks = (0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 10, 20, 40, 80, 160, 64, 512, 1280, 2560, 5120, 10240, 20480, 40960, 16384, 131072, 327680, 655360, 1310720, 2621440, 5242880, 10485760, 4194304, 33554432, 83886080, 167772160, 335544320, 671088640, 1342177280, 2684354560, 1073741824, 8589934592, 21474836480, 42949672960, 85899345920, 171798691840, 343597383680, 687194767360, 274877906944, 2199023255552, 5497558138880, 10995116277760, 21990232555520, 43980465111040, 87960930222080, 175921860444160, 70368744177664, 562949953421312, 1407374883553280, 2814749767106560, 5629499534213120, 11258999068426240, 22517998136852480, 45035996273704960, 18014398509481984)


####################################
# Pre-computed slider tables 
####################################
# Number of squares in direction to move from all squares
rook_unfull_rays = (282578800148862, 565157600297596, 1130315200595066, 2260630401190006, 4521260802379886, 9042521604759646, 18085043209519166, 36170086419038334, 282578800180736, 565157600328704, 1130315200625152, 2260630401218048, 4521260802403840, 9042521604775424, 18085043209518592, 36170086419037696, 282578808340736, 565157608292864, 1130315208328192, 2260630408398848, 4521260808540160, 9042521608822784, 18085043209388032, 36170086418907136, 282580897300736, 565159647117824, 1130317180306432, 2260632246683648, 4521262379438080, 9042522644946944, 18085043175964672, 36170086385483776, 283115671060736, 565681586307584, 1130822006735872, 2261102847592448, 4521664529305600, 9042787892731904, 18085034619584512, 36170077829103616, 420017753620736, 699298018886144, 1260057572672512, 2381576680245248, 4624614895390720, 9110691325681664, 18082844186263552, 36167887395782656, 35466950888980736, 34905104758997504, 34344362452452352, 33222877839362048, 30979908613181440, 26493970160820224, 17522093256097792, 35607136465616896, 9079539427579068672, 8935706818303361536, 8792156787827803136, 8505056726876686336, 7930856604974452736, 6782456361169985536, 4485655873561051136, 9115426935197958144)
bishop_unfull_rays = (18049651735527936, 70506452091904, 275415828992, 1075975168, 38021120, 8657588224, 2216338399232, 567382630219776, 9024825867763712, 18049651735527424, 70506452221952, 275449643008, 9733406720, 2216342585344, 567382630203392, 1134765260406784, 4512412933816832, 9024825867633664, 18049651768822272, 70515108615168, 2491752130560, 567383701868544, 1134765256220672, 2269530512441344, 2256206450263040, 4512412900526080, 9024834391117824, 18051867805491712, 637888545440768, 1135039602493440, 2269529440784384, 4539058881568768, 1128098963916800, 2256197927833600, 4514594912477184, 9592139778506752, 19184279556981248, 2339762086609920, 4538784537380864, 9077569074761728, 562958610993152, 1125917221986304, 2814792987328512, 5629586008178688, 11259172008099840, 22518341868716544, 9007336962655232, 18014673925310464, 2216338399232, 4432676798464, 11064376819712, 22137335185408, 44272556441600, 87995357200384, 35253226045952, 70506452091904, 567382630219776, 1134765260406784, 2832480465846272, 5667157807464448, 11333774449049600, 22526811443298304, 9024825867763712, 18049651735527936)
rook_full_rays = (72340172838076926, 144680345676153597, 289360691352306939, 578721382704613623, 1157442765409226991, 2314885530818453727, 4629771061636907199, 9259542123273814143, 72340172838141441, 144680345676217602, 289360691352369924, 578721382704674568, 1157442765409283856, 2314885530818502432, 4629771061636939584, 9259542123273813888, 72340172854657281, 144680345692602882, 289360691368494084, 578721382720276488, 1157442765423841296, 2314885530830970912, 4629771061645230144, 9259542123273748608, 72340177082712321, 144680349887234562, 289360695496279044, 578721386714368008, 1157442769150545936, 2314885534022901792, 4629771063767613504, 9259542123257036928, 72341259464802561, 144681423712944642, 289361752209228804, 578722409201797128, 1157443723186933776, 2314886351157207072, 4629771607097753664, 9259542118978846848, 72618349279904001, 144956323094725122, 289632270724367364, 578984165983651848, 1157687956502220816, 2315095537539358752, 4629910699613634624, 9259541023762186368, 143553341945872641, 215330564830528002, 358885010599838724, 645993902138460168, 1220211685215703056, 2368647251370188832, 4665518383679160384, 9259260648297103488, 18302911464433844481, 18231136449196065282, 18087586418720506884, 17800486357769390088, 17226286235867156496, 16077885992062689312, 13781085504453754944, 9187484529235886208)
bishop_full_rays = (9241421688590303744, 36099303471056128, 141012904249856, 550848566272, 6480472064, 1108177604608, 283691315142656, 72624976668147712, 4620710844295151618, 9241421688590368773, 36099303487963146, 141017232965652, 1659000848424, 283693466779728, 72624976676520096, 145249953336262720, 2310355422147510788, 4620710844311799048, 9241421692918565393, 36100411639206946, 424704217196612, 72625527495610504, 145249955479592976, 290499906664153120, 1155177711057110024, 2310355426409252880, 4620711952330133792, 9241705379636978241, 108724279602332802, 145390965166737412, 290500455356698632, 580999811184992272, 577588851267340304, 1155178802063085600, 2310639079102947392, 4693335752243822976, 9386671504487645697, 326598935265674242, 581140276476643332, 1161999073681608712, 288793334762704928, 577868148797087808, 1227793891648880768, 2455587783297826816, 4911175566595588352, 9822351133174399489, 1197958188344280066, 2323857683139004420, 144117404414255168, 360293502378066048, 720587009051099136, 1441174018118909952, 2882348036221108224, 5764696068147249408, 11529391036782871041, 4611756524879479810, 567382630219904, 1416240237150208, 2833579985862656, 5667164249915392, 11334324221640704, 22667548931719168, 45053622886727936, 18049651735527937)

# Combining into a tuple of tuples
white_pawn_doubles = (0,0,0,0,0,0,0,0, 16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
black_pawn_doubles = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4294967296, 8589934592, 17179869184, 34359738368, 68719476736, 137438953472, 274877906944, 549755813888, 0,0,0,0,0,0,0,0)


from utils import get_set_bit_indices, find_least_significant_bit_set, has_one_one, bit_to_numpy_array

# Precomputed bishop and rook moves without magic numbers (they are bits corresponding to moveable and capturing squares)

from utils import generate_bit_combinations, get_valid_piece_moves_including_captures, generate_one_bit_combinations, get_valid_piece_moves
long_precomputed_rook_table = []
for square in range(64):
    long_precomputed_rook_table.append({})
    blockers_bits = generate_bit_combinations(square, 'R')
    for blockers_bit in blockers_bits:
        valid_moves_bit = get_valid_piece_moves_including_captures(square, 'R', blockers_bit)
        long_precomputed_rook_table[square][blockers_bit] = valid_moves_bit


long_precomputed_bishop_table = []
for square in range(64):
    long_precomputed_bishop_table.append({})
    blockers_bits = generate_bit_combinations(square, 'B')
    for blockers_bit in blockers_bits:
        valid_moves_bit = get_valid_piece_moves_including_captures(square, 'B', blockers_bit)
        long_precomputed_bishop_table[square][blockers_bit] = valid_moves_bit

# Precomputed bishop and rook moves with only one blocker and only on the direction of blocker (for pins)

long_precomputed_rook_table_one_blocker = []
for square in range(64):
    long_precomputed_rook_table_one_blocker.append({})
    blockers_bits = generate_one_bit_combinations(rook_full_rays[square])
    for blockers_bit in blockers_bits:
        valid_moves_bit = get_valid_piece_moves(square, 'R', blockers_bit) & get_valid_piece_moves(find_least_significant_bit_set(blockers_bit), 'R', 2**square)
        long_precomputed_rook_table_one_blocker[square][blockers_bit] = valid_moves_bit | (2**square)


long_precomputed_bishop_table_one_blocker = []
for square in range(64):
    long_precomputed_bishop_table_one_blocker.append({})
    blockers_bits = generate_one_bit_combinations(bishop_full_rays[square])
    for blockers_bit in blockers_bits:
        valid_moves_bit = get_valid_piece_moves(square, 'B', blockers_bit) & get_valid_piece_moves(find_least_significant_bit_set(blockers_bit), 'B', 2**square)
        long_precomputed_bishop_table_one_blocker[square][blockers_bit] = valid_moves_bit | (2**square)


passant_bitboards = {-1: 0, 
                     16 : 65536, 17 : 131072, 18 : 262144, 19 : 524288, 20 : 1048576, 21 : 2097152, 22 : 4194304, 23: 8388608, 
                     40 : 1099511627776, 41 : 2199023255552, 42 : 4398046511104, 43 : 8796093022208, 44 : 17592186044416, 45 : 35184372088832, 46 : 70368744177664, 47 : 140737488355328}

######################
# Position class
######################

'''

ENGINE IDEAS:

- Tests:
Create a test for the engine where it may play against older versions of itself 1000 times. To
see improvements.

- New Transposition Tables: 
For transposition tables I am going to use Zobrist Hashing, which is a method of hasshing poitions as 
a bit integer. It performs much faster than hashing with the fen strings. However some positions may not 
be distinguished from other different positions, but these are too small a number.

- Add Late move reductions:
This reduces the depth of moves which are ordered last in the ordered_moves. Read more about it.

- Improve Iterative deepening:
hmmm...

- Keep alpha Beta
- Keep Killer moves
- Keep Quiescence search
'''

from collections import namedtuple
Move = namedtuple("Move", "i j prom capture")  # So to define a move we must do Move(square, destination_square, promotion(maybe use array index), moving_pieces_bit)

'''
wc, bc  # The castling rights, these will be lists of two Boolean variables. The first element
        # of the list represents kingside castle, the second queenside castle. They only check
        # if the king or rook has already moved (to check if there are in between checks we do
        # it in gen_moves method).

psquare  # An integer representing the square that can be captured using en passant.
        # It will be -1 if the last move wasn't a double pawn move.
        # I will change the passant variable every time a double pawn move is made in
        # the move method.

moving_piece # Integer representing moving piece. If less than 6 whites move, else blacks

capture_index # 6 pawn, 7 knight, 8 bishop, 9 rook, 10 queen

pins # A bitboard representing the 
'''
             
            
class BitPosition:
    def __init__(self, bitboard, turn, wc = [True, True], bc = [True, True], passant_square = -1):
        self.bitboard = bitboard  # list of 64-bit integers: w_pawns, w_knights, w_bishops, w_rooks, w_queens, w_king, b_pawns, ...
        self.turn = turn  # True if white's turn, False if black
        self.position_ply_info = [] # (wc, bc, psquare, pins, checks) 
        self.move_ply_info = [] # (moving_piece, capture_index)
        self.wc = wc # [Boolean, Boolean] represinting white kingside/ queenside castling rights
        self.bc = bc # [Boolean, Boolean] represinting black kingside/ queenside castling rights
        self.psquare = passant_square # Index of the en passant square (a1 = 0, h8 = 63) if there is no en passant square then it is set to -1.
        self.current_pins = (0,0)
        self.current_checks = (0,0,0,0,0,0)    

    def king_is_safe_after_passant(self, removed_square_1, removed_square_2):
        '''
        See if the king is in check or not (from kings position). For when moving the king.
        '''
        bitboard = self.bitboard
        if self.turn: # If whites turn
            king_position = find_least_significant_bit_set(bitboard[5])
            all_own_pieces_bit_without_king = (bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]) & ~(2**removed_square_1 | 2**removed_square_2)
            # Bishops
            if bitboard[8] != 0:
                moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_own_pieces_bit_without_king)]
                if moveable_squares & bitboard[8] != 0: # If there is a bishop giving check
                    return False
            # Rooks
            if bitboard[9] != 0:
                moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_own_pieces_bit_without_king)]
                if moveable_squares & bitboard[9] != 0: # If there is a rook giving check
                    return False
            # Queens
            if bitboard[10] != 0:
                straight_moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_own_pieces_bit_without_king)]
                diag_moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_own_pieces_bit_without_king)] 
                if straight_moveable_squares & bitboard[10] != 0: # If there is a queen giving check horizontally or vertically
                    return False
                if diag_moveable_squares & bitboard[10] != 0: # If there is a queen giving check diagonally
                    return False
            return True
        
        else: # If blacks turn
            king_position = find_least_significant_bit_set(bitboard[11])
            all_own_pieces_bit_without_king = (bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5] | bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10]) & ~(2**removed_square_1 | 2**removed_square_2)
            # Bishops
            if bitboard[2] != 0:
                moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_own_pieces_bit_without_king)]
                if moveable_squares & bitboard[2] != 0: # If there is a bishop giving check
                    return False
            # Rooks
            if bitboard[3] != 0:
                moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_own_pieces_bit_without_king)]
                if moveable_squares & bitboard[3] != 0: # If there is a rook giving check
                    return False
            # Queens
            if bitboard[4] != 0:
                straight_moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_own_pieces_bit_without_king)]
                diag_moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_own_pieces_bit_without_king)] 
                if straight_moveable_squares & bitboard[4] != 0: # If there is a queen giving check horizontally or vertically
                    return False
                if diag_moveable_squares & bitboard[4] != 0: # If there is a queen giving check diagonally
                    return False
            return True

    
    def king_is_safe(self, destination):
        '''
        See if the king is in check or not (from kings position). For when moving the king.
        '''
        bitboard = self.bitboard
        if self.turn: # If whites turn
            all_own_pieces_bit_without_king = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11] 
            # Pawns
            if bitboard[6] != 0: # For pawns we have to be carefull because they move upwards or downwards depending on whose turn it is
                attacking_squares = white_pawn_attacks[destination]
                if attacking_squares & bitboard[6] != 0:
                    return False
            # Knights
            if bitboard[7] != 0:
                moveable_squares = knight_moves[destination]
                if moveable_squares & bitboard[7] != 0: # If there is a knight giving check
                    return False
            # Bishops
            if bitboard[8] != 0:
                moveable_squares = long_precomputed_bishop_table[destination][bishop_unfull_rays[destination] & (all_own_pieces_bit_without_king)]
                if moveable_squares & bitboard[8] != 0: # If there is a bishop giving check
                    return False
            # King
            moveable_squares = king_moves[destination]
            if moveable_squares & bitboard[11] != 0: # If the king moved next to other king
                return False
            # Rooks
            if bitboard[9] != 0:
                moveable_squares = long_precomputed_rook_table[destination][rook_unfull_rays[destination] & (all_own_pieces_bit_without_king)]
                if moveable_squares & bitboard[9] != 0: # If there is a rook giving check
                    return False
            # Queens
            if bitboard[10] != 0:
                straight_moveable_squares = long_precomputed_rook_table[destination][rook_unfull_rays[destination] & (all_own_pieces_bit_without_king)]
                diag_moveable_squares = long_precomputed_bishop_table[destination][bishop_unfull_rays[destination] & (all_own_pieces_bit_without_king)] 
                if straight_moveable_squares & bitboard[10] != 0: # If there is a queen giving check horizontally or vertically
                    return False
                if diag_moveable_squares & bitboard[10] != 0: # If there is a queen giving check diagonally
                    return False
            return True
        
        else: # If blacks turn
            all_own_pieces_bit_without_king = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5] | bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10]
            # Pawns
            if bitboard[0] != 0: # For pawns we have to be carefull because they move upwards or downwards depending on whose turn it is
                attacking_squares = black_pawn_attacks[destination]
                if attacking_squares & bitboard[0] != 0:
                    return False
            # Knights
            if bitboard[1] != 0:
                moveable_squares = knight_moves[destination]
                if moveable_squares & bitboard[1] != 0: # If there is a knight giving check
                    return False
            # Bishops
            if bitboard[2] != 0:
                moveable_squares = long_precomputed_bishop_table[destination][bishop_unfull_rays[destination] & (all_own_pieces_bit_without_king)]
                if moveable_squares & bitboard[2] != 0: # If there is a bishop giving check
                    return False
            # King
            moveable_squares = king_moves[destination]
            if moveable_squares & bitboard[5] != 0: # If the king moved next to other king
                return False
            
            # Rooks
            if bitboard[3] != 0:
                moveable_squares = long_precomputed_rook_table[destination][rook_unfull_rays[destination] & (all_own_pieces_bit_without_king)]
                if moveable_squares & bitboard[3] != 0: # If there is a rook giving check
                    return False
            # Queens
            if bitboard[4] != 0:
                straight_moveable_squares = long_precomputed_rook_table[destination][rook_unfull_rays[destination] & (all_own_pieces_bit_without_king)]
                diag_moveable_squares = long_precomputed_bishop_table[destination][bishop_unfull_rays[destination] & (all_own_pieces_bit_without_king)] 
                if straight_moveable_squares & bitboard[4] != 0: # If there is a queen giving check horizontally or vertically
                    return False
                if diag_moveable_squares & bitboard[4] != 0: # If there is a queen giving check diagonally
                    return False
            return True
        
    def is_check(self):
        '''
        Count number of checks and if any slider checks return the bit corresponding to the ray of the slider giving check (To block it later).
        Since after making a check we store in the bitposition we have done so. Hence position has in_check attribute = True.
        We are going to check for checks more efficiently from the kings position and assuming it can move as any piece.
        '''
        bitboard = self.bitboard
        all_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5] | bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
        if self.turn:
            king_position = find_least_significant_bit_set(bitboard[5])

            # Queens
            if bitboard[10] != 0:
                all_moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_pieces_bit)] | long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_pieces_bit)] 
                if all_moveable_squares & bitboard[10] != 0: # If there is a queen giving check horizontally or vertically
                    return True              
            # Bishops
            if bitboard[8] != 0:
                moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_pieces_bit)]
                if moveable_squares & bitboard[8] != 0: # If there is a bishop giving check
                    return True
            # Rooks
            if bitboard[9] != 0:
                moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_pieces_bit)]
                if moveable_squares & bitboard[9] != 0: # If there is a rook giving check
                    return True
            # Pawns
            if bitboard[6] != 0: # For pawns we have to be carefull because they move upwards or downwards depending on whose turn it is
                attacking_squares = white_pawn_attacks[king_position]
                if attacking_squares & bitboard[6] != 0:
                    return True

            # Knights
            if bitboard[7] != 0:
                moveable_squares = knight_moves[king_position]
                if moveable_squares & bitboard[7] != 0: # If there is a knight giving check
                    return True
                
            return False # No checks
        
        else: # Blacks turn
            king_position = find_least_significant_bit_set(bitboard[11])

            # Queens
            if bitboard[4] != 0:
                all_moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_pieces_bit)] | long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_pieces_bit)] 
                if all_moveable_squares & bitboard[4] != 0: # If there is a queen giving check horizontally or vertically
                    return True
                
            # Bishops
            if bitboard[2] != 0:
                moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_pieces_bit)]
                if moveable_squares & bitboard[2] != 0: # If there is a bishop giving check
                    return True

            # Rooks 
            if bitboard[3] != 0:
                moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_pieces_bit)]
                if moveable_squares & bitboard[3] != 0: # If there is a rook giving check
                    return True

            # Pawns 
            if bitboard[0] != 0: # For pawns we have to be carefull because they move upwards or downwards depending on whose turn it is
                attacking_squares = black_pawn_attacks[king_position]
                if attacking_squares & bitboard[0] != 0:
                    return True

            # Knights 
            if bitboard[1] != 0:
                moveable_squares = knight_moves[king_position]
                if moveable_squares & bitboard[1] != 0: # If there is a knight giving check
                    return True

            return False # No checks
        
    def get_pins_bits(self):
        '''
        Get a bitboard of the pinned squares, these are squares containg pinned piece and the ray. We get two bitboards, one for straight pins and one for 
        diagonal pins. This makes generating legal moves easier, since the pinned sliders can move diagonally or straight depending if the pin is diagonal 
        or straight.
        '''
        bitboard = self.bitboard
        
        straight_pins = 0
        diagonal_pins = 0
        if self.turn:
            king_position = find_least_significant_bit_set(bitboard[5])
            all_own_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
            all_opp_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]

            # Bishop pins
            if bitboard[8] & bishop_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[8] & bishop_full_rays[king_position]):
                    bishop_ray = long_precomputed_bishop_table_one_blocker[square][bitboard[5]]
                    if has_one_one(bishop_ray & all_own_pieces_bit) and has_one_one(bishop_ray & all_opp_pieces_bit):
                        diagonal_pins |= bishop_ray
            
            # Rook pins
            if bitboard[9] & rook_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[9] & rook_full_rays[king_position]):
                    rook_ray = long_precomputed_rook_table_one_blocker[square][bitboard[5]]
                    if has_one_one(rook_ray & all_own_pieces_bit) and has_one_one(rook_ray & all_opp_pieces_bit):
                        straight_pins |= rook_ray
            
            # Queen pins
            if bitboard[10] & bishop_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[10] & bishop_full_rays[king_position]):
                    bishop_ray = long_precomputed_bishop_table_one_blocker[square][bitboard[5]]
                    if has_one_one(bishop_ray & all_own_pieces_bit) and has_one_one(bishop_ray & all_opp_pieces_bit):
                        diagonal_pins |= bishop_ray

            if bitboard[10] & rook_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[10] & rook_full_rays[king_position]):
                    rook_ray = long_precomputed_rook_table_one_blocker[square][bitboard[5]]
                    if has_one_one(rook_ray & all_own_pieces_bit) and has_one_one(rook_ray & all_opp_pieces_bit):
                        straight_pins |= rook_ray


        else:
            king_position = find_least_significant_bit_set(bitboard[11])
            all_own_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
            all_opp_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]

            # Bishop pins
            if bitboard[2] & bishop_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[2] & bishop_full_rays[king_position]):
                    bishop_ray = long_precomputed_bishop_table_one_blocker[square][bitboard[11]]
                    if has_one_one(bishop_ray & all_own_pieces_bit) and has_one_one(bishop_ray & all_opp_pieces_bit):
                        diagonal_pins |= bishop_ray
            
            # Rook pins
            if bitboard[3] & rook_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[3] & rook_full_rays[king_position]):
                    rook_ray = long_precomputed_rook_table_one_blocker[square][bitboard[11]]
                    if has_one_one(rook_ray & all_own_pieces_bit) and has_one_one(rook_ray & all_opp_pieces_bit):
                        straight_pins |= rook_ray
            
            # Queen pins
            if bitboard[4] & bishop_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[4] & bishop_full_rays[king_position]):
                    bishop_ray = long_precomputed_bishop_table_one_blocker[square][bitboard[11]]
                    if has_one_one(bishop_ray & all_own_pieces_bit) and has_one_one(bishop_ray & all_opp_pieces_bit):
                        diagonal_pins |= bishop_ray

            if bitboard[4] & rook_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[4] & rook_full_rays[king_position]):
                    rook_ray = long_precomputed_rook_table_one_blocker[square][bitboard[11]]
                    if has_one_one(rook_ray & all_own_pieces_bit) and has_one_one(rook_ray & all_opp_pieces_bit):
                        straight_pins |= rook_ray
        return diagonal_pins, straight_pins
    
    def new_checks_info(self):
        '''
        Get a bitboard of the pinned squares, these are squares containg pinned piece and the ray. We get two bitboards, one for straight pins and one for 
        diagonal pins. This makes generating legal moves easier, since the pinned sliders can move diagonally or straight depending if the pin is diagonal 
        or straight.
        '''
        bitboard = self.bitboard
        # Positions of pieces giving checks (one bitboard for each piece type)
        pawn_checks = 0
        knight_checks = 0
        bishop_checks = 0
        rook_checks = 0
        queen_checks = 0

        rays = 0 # Rays of sliders giving checks
        num_checks = 0 # Number of checks

        # Rays in which there is a pinned piece
        straight_pins = 0
        diagonal_pins = 0

        if self.turn:
            king_position = find_least_significant_bit_set(bitboard[5])
            all_own_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
            all_opp_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
            all_pieces_bit = all_own_pieces_bit | all_opp_pieces_bit

            # Pawns (Note we can only give check with one pawn at a time)
            # For pawns we have to be carefull because they move upwards or downwards depending on whose turn it is
            attacking_squares = white_pawn_attacks[king_position]
            if attacking_squares & bitboard[6] != 0:
                pawn_checks |= attacking_squares & bitboard[6]
                num_checks += 1

            # Knights (Note we can only give check with one knight at a time)
            moveable_squares = knight_moves[king_position]
            if moveable_squares & bitboard[7] != 0: # If there is a knight giving check
                knight_checks |= moveable_squares & bitboard[7]
                num_checks += 1

            # Bishop pins
            if bitboard[8] & bishop_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[8] & bishop_full_rays[king_position]):
                    bishop_ray = long_precomputed_bishop_table_one_blocker[square][bitboard[5]] # Ray from square where bishop is to king, including opponents bishop square (without taking into account blockers)
                    if has_one_one(bishop_ray & all_pieces_bit): # Check
                        bishop_checks |= bishop_ray & bitboard[8]
                        rays = bishop_ray & ~bitboard[8]
                        num_checks += 1
                    elif has_one_one(bishop_ray & all_own_pieces_bit) and has_one_one(bishop_ray & all_opp_pieces_bit): # Pin
                        diagonal_pins |= bishop_ray
            
            if num_checks == 2: # If there are two checks or more we may only move king hence other stuff like pins and rays don't need to be computed
                return (0, 0, 0, 0, 0, 0, 2), (0, 0)
            
            # Rook pins
            if bitboard[9] & rook_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[9] & rook_full_rays[king_position]):
                    rook_ray = long_precomputed_rook_table_one_blocker[square][bitboard[5]]
                    if has_one_one(rook_ray & all_pieces_bit): # Check
                        rook_checks |= rook_ray & bitboard[9]
                        rays = rook_ray & ~bitboard[9]
                        num_checks += 1
                    elif has_one_one(rook_ray & all_own_pieces_bit) and has_one_one(rook_ray & all_opp_pieces_bit): # Pin
                        straight_pins |= rook_ray
            

            
            # Queen pins
            if bitboard[10] & bishop_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[10] & bishop_full_rays[king_position]):
                    bishop_ray = long_precomputed_bishop_table_one_blocker[square][bitboard[5]]
                    if has_one_one(bishop_ray & all_pieces_bit): # Check
                        queen_checks |= bishop_ray & bitboard[10]
                        rays = bishop_ray & ~bitboard[10]
                        num_checks += 1
                    elif has_one_one(bishop_ray & all_own_pieces_bit) and has_one_one(bishop_ray & all_opp_pieces_bit): # Pin
                        diagonal_pins |= bishop_ray

            if bitboard[10] & rook_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[10] & rook_full_rays[king_position]):
                    rook_ray = long_precomputed_rook_table_one_blocker[square][bitboard[5]]
                    if has_one_one(rook_ray & all_pieces_bit): # Check
                        queen_checks |= rook_ray & bitboard[10]
                        rays = rook_ray & ~bitboard[10]
                        num_checks += 1
                    elif has_one_one(rook_ray & all_own_pieces_bit) and has_one_one(rook_ray & all_opp_pieces_bit): # Pin
                        straight_pins |= rook_ray


        else:
            king_position = find_least_significant_bit_set(bitboard[11])
            all_own_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
            all_opp_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
            all_pieces_bit = all_own_pieces_bit | all_opp_pieces_bit

            # Pawns (Note we can only give check with one pawn at a time)
            # For pawns we have to be carefull because they move upwards or downwards depending on whose turn it is
            attacking_squares = black_pawn_attacks[king_position]
            if attacking_squares & bitboard[0] != 0:
                pawn_checks |= attacking_squares & bitboard[0]
                num_checks += 1

            # Knights (Note we can only give check with one knight at a time)
            moveable_squares = knight_moves[king_position]
            if moveable_squares & bitboard[1] != 0: # If there is a knight giving check
                knight_checks |= moveable_squares & bitboard[1]
                num_checks += 1
                
            # Bishop pins
            if bitboard[2] & bishop_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[2] & bishop_full_rays[king_position]):
                    bishop_ray = long_precomputed_bishop_table_one_blocker[square][bitboard[11]]
                    if has_one_one(bishop_ray & all_pieces_bit): # Check
                        bishop_checks |= bishop_ray & bitboard[2]
                        rays = bishop_ray & ~bitboard[2]
                        num_checks += 1
                    elif has_one_one(bishop_ray & all_own_pieces_bit) and has_one_one(bishop_ray & all_opp_pieces_bit): # Pin
                        diagonal_pins |= bishop_ray
            
            if num_checks == 2: # If there are two checks or more we may only move king hence other stuff like pins and rays don't need to be computed
                return (0, 0, 0, 0, 0, 0, 2), (0,0)
            
            # Rook pins
            if bitboard[3] & rook_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[3] & rook_full_rays[king_position]):
                    rook_ray = long_precomputed_rook_table_one_blocker[square][bitboard[11]]
                    if has_one_one(rook_ray & all_pieces_bit): # Check
                        rook_checks |= rook_ray & bitboard[3]
                        rays = rook_ray & ~bitboard[3]
                        num_checks += 1
                    elif has_one_one(rook_ray & all_own_pieces_bit) and has_one_one(rook_ray & all_opp_pieces_bit): # Pin
                        straight_pins |= rook_ray
            
            # Queen pins
            if bitboard[4] & bishop_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[4] & bishop_full_rays[king_position]):
                    bishop_ray = long_precomputed_bishop_table_one_blocker[square][bitboard[11]]
                    if has_one_one(bishop_ray & all_pieces_bit): # Check
                        queen_checks |= bishop_ray & bitboard[4]
                        rays = bishop_ray & ~bitboard[4]
                        num_checks += 1
                    elif has_one_one(bishop_ray & all_own_pieces_bit) and has_one_one(bishop_ray & all_opp_pieces_bit): # Pin
                        diagonal_pins |= bishop_ray

            if bitboard[4] & rook_full_rays[king_position] != 0:
                for square in get_set_bit_indices(bitboard[4] & rook_full_rays[king_position]):
                    rook_ray = long_precomputed_rook_table_one_blocker[square][bitboard[11]]
                    if has_one_one(rook_ray & all_pieces_bit): # Check
                        queen_checks |= rook_ray & bitboard[4]
                        rays = rook_ray & ~bitboard[4]
                        num_checks += 1
                    elif has_one_one(rook_ray & all_own_pieces_bit) and has_one_one(rook_ray & all_opp_pieces_bit): # Pin
                        straight_pins |= rook_ray
        return (pawn_checks, knight_checks, bishop_checks, rook_checks, queen_checks, rays, num_checks), (diagonal_pins, straight_pins)
    
    def get_checks_info(self):
        '''
        Count number of checks and if any slider checks return the bit corresponding to the ray of the slider giving check (To block it later).
        Since after making a check we store in the bitposition we have done so. Hence position has in_check attribute = True.
        We are going to check for checks more efficiently from the kings position and assuming it can move as any piece.
        '''
        bitboard = self.bitboard
        all_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5] | bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
        # Positions of pieces giving checks (one bitboard for each piece type)
        pawn_checks = 0
        knight_checks = 0
        bishop_checks = 0
        rook_checks = 0
        queen_checks = 0

        rays = 0 # Rays of sliders giving checks
        num_checks = 0 # Number of checks
        if self.turn:
            king_position = find_least_significant_bit_set(bitboard[5])
            
            # Pawns (Note we can only give check with one pawn at a time)
            # For pawns we have to be carefull because they move upwards or downwards depending on whose turn it is
            attacking_squares = white_pawn_attacks[king_position]
            if attacking_squares & bitboard[6] != 0:
                pawn_checks |= attacking_squares & bitboard[6]
                num_checks += 1

            # Knights (Note we can only give check with one knight at a time)
            moveable_squares = knight_moves[king_position]
            if moveable_squares & bitboard[7] != 0: # If there is a knight giving check
                knight_checks |= moveable_squares & bitboard[7]
                num_checks += 1

            # Bishops (Note we can only give check with one bishop at a time)
            if bitboard[8] != 0:
                moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_pieces_bit)] # Ray from king position up to and including pieces that block
                if moveable_squares & bitboard[8] != 0: # If there is a bishop giving check
                    bishop_position = find_least_significant_bit_set(moveable_squares & bitboard[8]) # There can only be one bishop giving check
                    rays = moveable_squares & long_precomputed_bishop_table[bishop_position][bishop_unfull_rays[bishop_position] & (all_pieces_bit)]
                    bishop_checks |= moveable_squares & bitboard[8]
                    num_checks += 1

            # Rooks (Note we can only give check with one rook at a time)
            if bitboard[9] != 0:
                moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_pieces_bit)]
                if moveable_squares & bitboard[9] != 0: # If there is a rook giving check
                    rook_position = find_least_significant_bit_set(moveable_squares & bitboard[9]) # There can only be one rook giving check
                    rays = moveable_squares & long_precomputed_rook_table[rook_position][rook_unfull_rays[rook_position] & (all_pieces_bit)]
                    rook_checks |= moveable_squares & bitboard[9]
                    num_checks += 1

            # Queens (Note we can give only give check with one queen at a time)
            if bitboard[10] != 0:
                straight_moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_pieces_bit)]
                diag_moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_pieces_bit)] 
                if straight_moveable_squares & bitboard[10] != 0: # If there is a queen giving check horizontally or vertically
                    queen_position = find_least_significant_bit_set(straight_moveable_squares & bitboard[10])
                    rays = straight_moveable_squares & long_precomputed_rook_table[queen_position][rook_unfull_rays[queen_position] & (all_pieces_bit)]
                    queen_checks |= straight_moveable_squares & bitboard[10]
                    num_checks += 1
                if diag_moveable_squares & bitboard[10] != 0: # If there is a queen giving check diagonally
                    queen_position = find_least_significant_bit_set(diag_moveable_squares & bitboard[10])
                    rays = diag_moveable_squares & long_precomputed_bishop_table[queen_position][bishop_unfull_rays[queen_position] & (all_pieces_bit)]
                    queen_checks |= diag_moveable_squares & bitboard[10]
                    num_checks += 1

            return pawn_checks, knight_checks, bishop_checks, rook_checks, queen_checks, rays, num_checks
        
        else: # Blacks turn
            king_position = find_least_significant_bit_set(bitboard[11])

            # Pawns (Note we can only give check with one pawn at a time)
            # For pawns we have to be carefull because they move upwards or downwards depending on whose turn it is
            attacking_squares = black_pawn_attacks[king_position]
            if attacking_squares & bitboard[0] != 0:
                pawn_checks |= attacking_squares & bitboard[0]
                num_checks += 1

            # Knights (Note we can only give check with one knight at a time)
            moveable_squares = knight_moves[king_position]
            if moveable_squares & bitboard[1] != 0: # If there is a knight giving check
                knight_checks |= moveable_squares & bitboard[1]
                num_checks += 1

            # Bishops (Note we can only give check with one bishop at a time)
            if bitboard[2] != 0:
                moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_pieces_bit)]
                if moveable_squares & bitboard[2] != 0: # If there is a bishop giving check
                    bishop_position = find_least_significant_bit_set(moveable_squares & bitboard[2]) # There can only be one bishop giving check
                    rays = moveable_squares & long_precomputed_bishop_table[bishop_position][bishop_unfull_rays[bishop_position] & (all_pieces_bit)]
                    bishop_checks |= moveable_squares & bitboard[2]
                    num_checks += 1

            # Rooks (Note we can only give check with one rook at a time)
            if bitboard[3] != 0:
                moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_pieces_bit)]
                if moveable_squares & bitboard[3] != 0: # If there is a rook giving check
                    rook_position = find_least_significant_bit_set(moveable_squares & bitboard[3]) # There can only be one rook giving check
                    rays = moveable_squares & long_precomputed_rook_table[rook_position][rook_unfull_rays[rook_position] & (all_pieces_bit)]
                    rook_checks |= moveable_squares & bitboard[3]
                    num_checks += 1

            # Queens (Note we can give only give check with one queen at a time)
            if bitboard[4] != 0:
                straight_moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_pieces_bit)]
                diag_moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_pieces_bit)] 
                if straight_moveable_squares & bitboard[4] != 0: # If there is a queen giving check horizontally or vertically
                    queen_position = find_least_significant_bit_set(straight_moveable_squares & bitboard[4])
                    rays = straight_moveable_squares & long_precomputed_rook_table[queen_position][rook_unfull_rays[queen_position] & (all_pieces_bit)]
                    queen_checks |= straight_moveable_squares & bitboard[4]
                    num_checks += 1
                if diag_moveable_squares & bitboard[4] != 0: # If there is a queen giving check diagonally
                    queen_position = find_least_significant_bit_set(diag_moveable_squares & bitboard[4])
                    rays = diag_moveable_squares & long_precomputed_bishop_table[queen_position][bishop_unfull_rays[queen_position] & (all_pieces_bit)]
                    queen_checks |= diag_moveable_squares & bitboard[4]
                    num_checks += 1

            return pawn_checks, knight_checks, bishop_checks, rook_checks, queen_checks, rays, num_checks
    
    def in_check_captures(self):
        '''
        We are going to check for checks more efficiently from the kings position and assuming it can move as any piece.
        This will yield the moves to reduce computational time.
        '''
        bitboard = self.bitboard
        self.current_checks, self.current_pins = self.new_checks_info()
        all_pins = self.current_pins[0] | self.current_pins[1]
        captures = []
        if self.turn: # If whites turn

            all_own_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
            all_pieces_bit = all_own_pieces_bit | bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
        
            # We go piece by piece yielding captures
            # Capturing with King
            piece_bit = bitboard[5]
            origin_square = find_least_significant_bit_set(piece_bit) # We get the indices of the squares pieces of this type are in
            for i in range(6,12):
                capture_check_squares = king_moves[origin_square] & bitboard[i] # We get the precomputed moveable squares
                if capture_check_squares != 0: # If we can capture
                    for destination in get_set_bit_indices(capture_check_squares):
                        if self.king_is_safe(destination):
                            captures.append(Move(origin_square, destination, 0, i))

            if self.current_checks[-1] == 1: # We can only capture (with a piece that is not the king) or block if there is only one check
                # Capturing with Pawns
                piece_bit = bitboard[0] & ~all_pins
                if piece_bit != 0: # If we can't move pawns
                    for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                        for i in range(5):
                            capture_check_squares = white_pawn_attacks[origin_square] & self.current_checks[i] # We get the precomputed moveable squares
                            if capture_check_squares != 0: # If we can capture pieces giving check
                                destination = find_least_significant_bit_set(capture_check_squares) # There's only one check
                                if destination > 55:
                                    captures.append(Move(origin_square, destination, 4, i + 6))
                                    captures.append(Move(origin_square, destination, 3, i + 6))
                                    captures.append(Move(origin_square, destination, 2, i + 6)) 
                                    captures.append(Move(origin_square, destination, 1, i + 6))
                                else:
                                    captures.append(Move(origin_square, destination, 0, i + 6))
                        if white_pawn_attacks[origin_square] & passant_bitboards[self.psquare] != 0 and self.king_is_safe_after_passant(origin_square, self.psquare-8): # En passant capture
                            captures.append(Move(origin_square, self.psquare, 0, 6))

                # Capturing with knights
                piece_bit = bitboard[1] & ~all_pins
                if piece_bit != 0: # If we have no pieces of the current type
                    for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                        for i in range(5):
                            capture_check_squares = knight_moves[origin_square] & self.current_checks[i] # We get the precomputed moveable squares
                            if capture_check_squares != 0: # If we can capture
                                captures.append(Move(origin_square, find_least_significant_bit_set(capture_check_squares), 0, i + 6))
                

                # Capturing with Rooks
                piece_bit = bitboard[3] & ~all_pins
                if piece_bit != 0:
                    for origin_square in get_set_bit_indices(piece_bit):
                        for i in range(5):
                            capture_check_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)] & self.current_checks[i]
                            if capture_check_squares != 0:
                                captures.append(Move(origin_square, find_least_significant_bit_set(capture_check_squares), 0, i + 6))

                # Capturing with Bishops
                piece_bit = bitboard[2] & ~all_pins
                if piece_bit != 0:
                    for origin_square in get_set_bit_indices(piece_bit):
                        for i in range(5):
                            capture_check_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)] & self.current_checks[i]
                            if capture_check_squares != 0:
                                captures.append(Move(origin_square, find_least_significant_bit_set(capture_check_squares), 0, i + 6))
                
                # Capturing with Queens
                piece_bit = bitboard[4] & ~all_pins
                if piece_bit != 0:
                    for origin_square in get_set_bit_indices(piece_bit):
                        for i in range(5):
                            capture_check_squares = (long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)] | long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]) & self.current_checks[i]
                            if capture_check_squares != 0:
                                captures.append(Move(origin_square, find_least_significant_bit_set(capture_check_squares), 0, i + 6))
        
        else: # Blacks turn
            all_own_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
            all_pieces_bit = all_own_pieces_bit | bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
        
            # We go piece by piece yielding captures
            # Capturing with King
            piece_bit = bitboard[11]
            origin_square = find_least_significant_bit_set(piece_bit) # We get the indices of the squares pieces of this type are in
            for i in range(5):
                capture_check_squares = king_moves[origin_square] & bitboard[i] # We get the precomputed moveable squares
                if capture_check_squares != 0: # If we can capture
                    for destination in get_set_bit_indices(capture_check_squares):
                        if self.king_is_safe(destination):
                            captures.append(Move(origin_square, destination, 0, i+6))

            if self.current_checks[-1] == 1: # We can only capture (with a piece that is not the king) or block if there is only one check
                # Capturing with Pawns
                piece_bit = bitboard[6] & ~all_pins
                if piece_bit != 0: # If we can't move pawns
                    for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                        for i in range(5):
                            capture_check_squares = black_pawn_attacks[origin_square] & self.current_checks[i] # We get the precomputed moveable squares
                            if capture_check_squares != 0: # If we can capture pieces giving check
                                destination = find_least_significant_bit_set(capture_check_squares) # There's only one check
                                if destination > 55:
                                    captures.append(Move(origin_square, destination, 4, i + 6))
                                    captures.append(Move(origin_square, destination, 3, i + 6))
                                    captures.append(Move(origin_square, destination, 2, i + 6)) 
                                    captures.append(Move(origin_square, destination, 1, i + 6))
                                else:
                                    captures.append(Move(origin_square, destination, 0, i + 6))
                        if black_pawn_attacks[origin_square] & passant_bitboards[self.psquare] != 0 and self.king_is_safe_after_passant(origin_square, self.psquare+8): # En passant capture (ply_info[-1][2] = psquare)
                            captures.append(Move(origin_square, self.psquare, 0, 6))

                # Capturing with knights
                piece_bit = bitboard[7] & ~all_pins
                if piece_bit != 0: # If we have no pieces of the current type
                    for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                        for i in range(5):
                            capture_check_squares = knight_moves[origin_square] & self.current_checks[i] # We get the precomputed moveable squares
                            if capture_check_squares != 0: # If we can capture
                                captures.append(Move(origin_square, find_least_significant_bit_set(capture_check_squares), 0, i + 6))
                

                # Capturing with Rooks
                piece_bit = bitboard[9] & ~all_pins
                if piece_bit != 0:
                    for origin_square in get_set_bit_indices(piece_bit):
                        for i in range(5):
                            capture_check_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)] & self.current_checks[i]
                            if capture_check_squares != 0:
                                captures.append(Move(origin_square, find_least_significant_bit_set(capture_check_squares), 0, i + 6))

                # Capturing with Bishops
                piece_bit = bitboard[8] & ~all_pins
                if piece_bit != 0:
                    for origin_square in get_set_bit_indices(piece_bit):
                        for i in range(5):
                            capture_check_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)] & self.current_checks[i]
                            if capture_check_squares != 0:
                                captures.append(Move(origin_square, find_least_significant_bit_set(capture_check_squares), 0, i + 6))
                
                # Capturing with Queens
                piece_bit = bitboard[10] & ~all_pins
                if piece_bit != 0:
                    for origin_square in get_set_bit_indices(piece_bit):
                        for i in range(5):
                            capture_check_squares = (long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)] | long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]) & self.current_checks[i]
                            if capture_check_squares != 0:
                                captures.append(Move(origin_square, find_least_significant_bit_set(capture_check_squares), 0, i + 6))
            
        return [move for move in sorted(captures, key=lambda move: move.capture, reverse=True)] # return the moves ordered in terms of the score and make is_check = 0 for all


    def in_check_moves(self):
        '''
        We are going to check for checks more efficiently from the kings position and assuming it can move as any piece.
        This will yield the moves to reduce computational time.
        '''
        bitboard = self.bitboard
        _, _, _, _, _, rays, num_checks = self.current_checks
        all_pins = self.current_pins[0] | self.current_pins[1]
        all_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5] | bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
        
        if self.turn: # If whites turn
        
            # We go piece by piece yielding blocking moves

            if num_checks == 1: # We can only capture (with a piece that is not the king) or block if there is only one check
                # Blocking with Pawns
                piece_bit = bitboard[0] & ~all_pins
                if piece_bit != 0: # If we can't move pawns
                    pawn_indices = get_set_bit_indices(piece_bit) # The indices of the squares the pawns are in
                    for origin_square in pawn_indices: # For position of piece of this type
                        if white_pawn_moves[origin_square] & all_pieces_bit == 0: # We can move the pawn
                            moveable_check_squares = white_pawn_moves[origin_square] & rays # We get the precomputed moveable squares
                            if moveable_check_squares != 0: # If we can capture pieces giving check
                                for destination in get_set_bit_indices(moveable_check_squares):
                                    if destination > 55:
                                            yield Move(origin_square, destination, 4, 0)
                                            yield Move(origin_square, destination, 3, 0) 
                                            yield Move(origin_square, destination, 2, 0) 
                                            yield Move(origin_square, destination, 1, 0)
                                    else:
                                        yield Move(origin_square, destination, 0, 0) # checks will have odd is_check attribute
                        if origin_square < 16 and white_pawn_doubles[origin_square] & rays != 0:
                            yield Move(origin_square, origin_square + 16, 0, 0)

                # Blocking with knights
                piece_bit = bitboard[1] & ~all_pins
                if piece_bit != 0: # If we have no pieces of the current type
                    bit_indices = get_set_bit_indices(piece_bit) # We get the indices of the squares pieces of this type are in
                    for origin_square in bit_indices: # For position of piece of this type
                        block_check_squares = knight_moves[origin_square] & rays # We get the precomputed moveable squares
                        if block_check_squares != 0: # If we can capture
                            for destination in get_set_bit_indices(block_check_squares):
                                yield Move(origin_square, destination, 0, 0) 

                # Blocking with Rooks
                piece_bit = bitboard[3] & ~all_pins
                if piece_bit != 0:
                    bit_indices = get_set_bit_indices(piece_bit)
                    for origin_square in bit_indices:
                        block_check_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)] & rays
                        if block_check_squares != 0:
                            for destination in get_set_bit_indices(block_check_squares):
                                yield Move(origin_square, destination, 0, 0)

                # Blocking with Bishops
                piece_bit = bitboard[2] & ~all_pins
                if piece_bit != 0:
                    bit_indices = get_set_bit_indices(piece_bit)
                    for origin_square in bit_indices:
                        block_check_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)] & rays
                        if block_check_squares != 0:
                            for destination in get_set_bit_indices(block_check_squares):
                                yield Move(origin_square, destination, 0, 0) 
                
                # Blocking with Queens
                piece_bit = bitboard[4] & ~all_pins
                if piece_bit != 0:
                    bit_indices = get_set_bit_indices(piece_bit)
                    for origin_square in bit_indices:
                        block_check_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                        block_check_squares |= long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                        block_check_squares &= rays
                        if block_check_squares != 0:
                            for destination in get_set_bit_indices(block_check_squares):
                                yield Move(origin_square, destination, 0, 0)
            
            # Moving king
            piece_bit = bitboard[5]
            origin_square = find_least_significant_bit_set(piece_bit) # We get the indices of the squares pieces of this type are in
            non_capture_check_squares = king_moves[origin_square] & ~(all_pieces_bit| rays) # We get the precomputed moveable squares
            if non_capture_check_squares != 0: # If we can capture
                for destination in get_set_bit_indices(non_capture_check_squares):
                    if self.king_is_safe(destination):
                        yield Move(origin_square, destination, 0, 0)
        
        else: # Blacks turn
        
            # We go piece by piece yielding blocking moves

            if num_checks == 1: # We can only capture (with a piece that is not the king) or block if there is only one check
                # Blocking with Pawns
                piece_bit = bitboard[6] & ~all_pins
                if piece_bit != 0: # If we can't move pawns
                    pawn_indices = get_set_bit_indices(piece_bit) # The indices of the squares the pawns are in
                    for origin_square in pawn_indices: # For position of piece of this type
                        if black_pawn_moves[origin_square] & all_pieces_bit == 0: # We can move the pawn
                            moveable_check_squares = black_pawn_moves[origin_square] & rays # We get the precomputed moveable squares
                            if moveable_check_squares != 0: # If we can capture pieces giving check
                                for destination in get_set_bit_indices(moveable_check_squares):
                                    if destination < 8:
                                            yield Move(origin_square, destination, 4, 0)
                                            yield Move(origin_square, destination, 3, 0) 
                                            yield Move(origin_square, destination, 2, 0) 
                                            yield Move(origin_square, destination, 1, 0)
                                    else:
                                        yield Move(origin_square, destination, 0, 0) # checks will have odd is_check attribute
                        if origin_square > 47 and black_pawn_doubles[origin_square] & rays != 0:
                            yield Move(origin_square, origin_square - 16, 0, 0)

                # Blocking with knights
                piece_bit = bitboard[7] & ~all_pins
                if piece_bit != 0: # If we have no pieces of the current type
                    bit_indices = get_set_bit_indices(piece_bit) # We get the indices of the squares pieces of this type are in
                    for origin_square in bit_indices: # For position of piece of this type
                        block_check_squares = knight_moves[origin_square] & rays # We get the precomputed moveable squares
                        if block_check_squares != 0: # If we can capture
                            for destination in get_set_bit_indices(block_check_squares):
                                yield Move(origin_square, destination, 0, 0) 

                # Blocking with Rooks
                piece_bit = bitboard[9] & ~all_pins
                if piece_bit != 0:
                    bit_indices = get_set_bit_indices(piece_bit)
                    for origin_square in bit_indices:
                        block_check_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)] & rays
                        if block_check_squares != 0:
                            for destination in get_set_bit_indices(block_check_squares):
                                yield Move(origin_square, destination, 0, 0)

                # Blocking with Bishops
                piece_bit = bitboard[8] & ~all_pins
                if piece_bit != 0:
                    bit_indices = get_set_bit_indices(piece_bit)
                    for origin_square in bit_indices:
                        block_check_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)] & rays
                        if block_check_squares != 0:
                            for destination in get_set_bit_indices(block_check_squares):
                                yield Move(origin_square, destination, 0, 0) 
                
                # Blocking with Queens
                piece_bit = bitboard[10] & ~all_pins
                if piece_bit != 0:
                    bit_indices = get_set_bit_indices(piece_bit)
                    for origin_square in bit_indices:
                        block_check_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                        block_check_squares |= long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                        block_check_squares &= rays
                        if block_check_squares != 0:
                            for destination in get_set_bit_indices(block_check_squares):
                                yield Move(origin_square, destination, 0, 0)
            
            # Moving king
            piece_bit = bitboard[11]
            origin_square = find_least_significant_bit_set(piece_bit) # We get the indices of the squares pieces of this type are in
            non_capture_check_squares = king_moves[origin_square] & ~(all_pieces_bit| rays) # We get the precomputed moveable squares
            if non_capture_check_squares != 0: # If we can capture
                for destination in get_set_bit_indices(non_capture_check_squares):
                    if self.king_is_safe(destination):
                        yield Move(origin_square, destination, 0, 0)

        


    def capture_moves(self):
        '''
        We create a set of moves and order them in terms of the score, returning a tuple of moves. This set of moves will always be computed before
        non_capture_moves so in this one we compute the next_unsafe_squares.
        '''
        bitboard = self.bitboard
        self.current_pins = self.get_pins_bits() # Computes the pins and stores the in self.pins and self.fake_pins (so that in non capture moves it is not necessary to compute)
        diagonal_pins, straight_pins = self.current_pins # Add pins to pins_ply so that we don't have to store them inside bitposition
        full_pins = diagonal_pins | straight_pins
        captures = []

        if self.turn: # If whites turn
            all_own_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
            all_opp_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
            all_pieces_bit = all_own_pieces_bit | all_opp_pieces_bit

            # Capturing with knight that are not pinned
            piece_bit = bitboard[1] & ~full_pins
            if piece_bit != 0: # If we have no pieces of the current type
                bit_indices = get_set_bit_indices(piece_bit) # We get the indices of the squares pieces of this type are in
                for origin_square in bit_indices: # For position of piece of this type
                    moveable_squares = knight_moves[origin_square] # We get the precomputed moveable squares
                    if moveable_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
                        for index in range(6,11): # For each of our opponent pieces, except king
                            capture_squares = moveable_squares & bitboard[index] # We get only squares in which opponent pieces are
                            if capture_squares != 0: # If we can capture
                                for destination in get_set_bit_indices(capture_squares):
                                    captures.append((index-1, Move(origin_square, destination, 0, index))) # non-checks will have even is_check attribute 

            # Capturing with king
            piece_bit = bitboard[5]
            origin_square = find_least_significant_bit_set(piece_bit) # We get the indices of the squares pieces of this type are in
            moveable_squares = king_moves[origin_square] # We get the precomputed moveable squares
            if moveable_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
                for index in range(6,11): # For each of our opponent pieces, except king
                    capture_squares = moveable_squares & bitboard[index] # We get only squares in which opponent pieces are
                    if capture_squares != 0: # If we can capture
                        for destination in get_set_bit_indices(capture_squares):
                            if self.king_is_safe(destination):
                                captures.append((index, Move(origin_square, destination, 0, index)))

            # Capturing with rook that are not pinned
            piece_bit = bitboard[3] & ~full_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    if moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(6,11):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-3, Move(origin_square, destination, 0, index))) # checks will have odd is_check attribute

            # Capturing with bishop that are not pinned
            piece_bit = bitboard[2] & ~full_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    if moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(6,11):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-2, Move(origin_square, destination, 0, index))) # checks will have odd is_check attribute
            
            # Capturing with queen that are not pinned
            piece_bit = bitboard[4] & ~full_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares |= long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    if moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(6,11):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-4, Move(origin_square, destination, 0, index))) # checks will have odd is_check attribute
            
            # Capturing with pawns that are not pinned
            piece_bit = bitboard[0] & ~full_pins
            if piece_bit != 0: # If we can't move pawns
                pawn_indices = get_set_bit_indices(piece_bit) # The indices of the squares the pawns are in
                for origin_square in pawn_indices: # For position of piece of this type
                    attacking_squares = white_pawn_attacks[origin_square] # We get the precomputed moveable squares
                    if attacking_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
                        for index in range(6,11): # For each of our opponent pieces, except king
                            capture_squares = attacking_squares & bitboard[index] # We get only squares in which opponent pieces are
                            if capture_squares != 0: # If we can capture
                                for destination in get_set_bit_indices(capture_squares):
                                    if destination > 55:
                                        captures.extend([(index, Move(origin_square, destination, 4, index)), (index, Move(origin_square, destination, 3, index)), 
                                                        (index, Move(origin_square, destination, 2, index)), (index, Move(origin_square, destination, 1, index))])
                                    else:
                                        captures.append((index, Move(origin_square, destination, 0, index))) # checks will have odd is_check attribute
                    if attacking_squares & passant_bitboards[self.psquare] != 0 and self.king_is_safe_after_passant(origin_square, self.psquare-8): # En passant capture (ply_info[-1][2] = psquare)
                        captures.append((0, Move(origin_square, self.psquare, 0, 6)))


            # Capturing with pinned pieces

            # Capturing with bishop that is pinned
            piece_bit = bitboard[2] & diagonal_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)] & diagonal_pins
                    if moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(6,11):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-2, Move(origin_square, destination, 0, index))) # checks will have odd is_check attribute
            
            # Capturing with rook that is pinned
            piece_bit = bitboard[3] & straight_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)] & straight_pins
                    if moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(6,11):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-3, Move(origin_square, destination, 0, index))) # checks will have odd is_check attribute

            # Capturing with queen that is pinned
            piece_bit = bitboard[4] & full_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    diag_moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)] & diagonal_pins
                    straight_moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)] & straight_pins
                    if diag_moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(6,11):
                            capture_squares = diag_moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-4,Move(origin_square, destination, 0, index))) # checks will have odd is_check attribute
                    if straight_moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(6,11):
                            capture_squares = straight_moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-4, Move(origin_square, destination, 0, index))) # checks will have odd is_check attribute
            
            # Capturing with pawns that are pinned
            piece_bit = bitboard[0] & diagonal_pins
            if piece_bit != 0: # If we can't move pawns
                pawn_indices = get_set_bit_indices(piece_bit) # The indices of the squares the pawns are in
                for origin_square in pawn_indices: # For position of piece of this type
                    attacking_squares = white_pawn_attacks[origin_square] & diagonal_pins # We get the precomputed moveable squares
                    if attacking_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
                        for index in range(6,11): # For each of our opponent pieces, except king
                            capture_squares = attacking_squares & bitboard[index] # We get only squares in which opponent pieces are
                            if capture_squares != 0: # If we can capture
                                for destination in get_set_bit_indices(capture_squares):
                                    if destination > 55:
                                        captures.extend([(index, Move(origin_square, destination, 4, index)), (index, Move(origin_square, destination, 3, index)), 
                                                        (index, Move(origin_square, destination, 2, index)), (index, Move(origin_square, destination, 1, index))])
                                    else:
                                        captures.append((index, Move(origin_square, destination, 0, index))) # checks will have odd is_check attribute

            return [move[1] for move in sorted(captures, key=lambda move: move[0], reverse=True)] # return the moves ordered in terms of the score and make is_check = 0 for all

        else: # Blacks turn
            all_opp_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
            all_own_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
            all_pieces_bit = all_own_pieces_bit | all_opp_pieces_bit

            # Capturing with knight that are not pinned
            piece_bit = bitboard[7] & ~full_pins
            if piece_bit != 0: # If we have no pieces of the current type
                bit_indices = get_set_bit_indices(piece_bit) # We get the indices of the squares pieces of this type are in
                for origin_square in bit_indices: # For position of piece of this type
                    moveable_squares = knight_moves[origin_square] # We get the precomputed moveable squares
                    if moveable_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
                        for index in range(5): # For each of our opponent pieces, except king
                            capture_squares = moveable_squares & bitboard[index] # We get only squares in which opponent pieces are
                            if capture_squares != 0: # If we can capture
                                for destination in get_set_bit_indices(capture_squares):
                                    captures.append((index-1, Move(origin_square, destination, 0, index+6))) # non-checks will have even is_check attribute 

            # Capturing with king
            piece_bit = bitboard[11]
            origin_square = find_least_significant_bit_set(piece_bit) # We get the indices of the squares pieces of this type are in
            moveable_squares = king_moves[origin_square] # We get the precomputed moveable squares
            if moveable_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
                for index in range(5): # For each of our opponent pieces, except king
                    capture_squares = moveable_squares & bitboard[index] # We get only squares in which opponent pieces are
                    if capture_squares != 0: # If we can capture
                        for destination in get_set_bit_indices(capture_squares):
                            if self.king_is_safe(destination):
                                captures.append((index, Move(origin_square, destination, 0, index+6)))

            # Capturing with rook that are not pinned
            piece_bit = bitboard[9] & ~full_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    if moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(5):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-3, Move(origin_square, destination, 0, index+6))) # checks will have odd is_check attribute

            # Capturing with bishop that are not pinned
            piece_bit = bitboard[8] & ~full_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    if moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(5):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-2, Move(origin_square, destination, 0, index+6))) # checks will have odd is_check attribute
            
            # Capturing with queen that are not pinned
            piece_bit = bitboard[10] & ~full_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares |= long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    if moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(5):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-4, Move(origin_square, destination, 0, index+6))) # checks will have odd is_check attribute
            
            # Capturing with pawns that are not pinned
            piece_bit = bitboard[6] & ~full_pins
            if piece_bit != 0: # If we can't move pawns
                pawn_indices = get_set_bit_indices(piece_bit) # The indices of the squares the pawns are in
                for origin_square in pawn_indices: # For position of piece of this type
                    attacking_squares = black_pawn_attacks[origin_square] # We get the precomputed moveable squares
                    if attacking_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
                        for index in range(5): # For each of our opponent pieces, except king
                            capture_squares = attacking_squares & bitboard[index] # We get only squares in which opponent pieces are
                            if capture_squares != 0: # If we can capture
                                for destination in get_set_bit_indices(capture_squares):
                                    if destination < 8:
                                        captures.extend([(index, Move(origin_square, destination, 4, index+6)), (index, Move(origin_square, destination, 3, index+6)), 
                                                        (index, Move(origin_square, destination, 2, index+6)), (index, Move(origin_square, destination, 1, index+6))])
                                    else:
                                        captures.append((index, Move(origin_square, destination, 0, index+6))) # checks will have odd is_check attribute

                    if attacking_squares & passant_bitboards[self.psquare] != 0 and self.king_is_safe_after_passant(origin_square, self.psquare+8): # En passant capture (ply_info[-1][2] = psquare)
                        captures.append((0, Move(origin_square, self.psquare, 0, 6)))


            # Capturing with pinned pieces

            # Capturing with bishop that are pinned
            piece_bit = bitboard[8] & diagonal_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)] & diagonal_pins
                    if moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(5):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-2, Move(origin_square, destination, 0, index+6))) # checks will have odd is_check attribute

            # Capturing with rook that are pinned
            piece_bit = bitboard[9] & straight_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)] & straight_pins
                    if moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(5):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-3, Move(origin_square, destination, 0, index+6))) # checks will have odd is_check attribute
            
            # Capturing with queen that are pinned
            piece_bit = bitboard[10] & full_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    diagonal_moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)] & diagonal_pins
                    straight_moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)] & straight_pins
                    if diagonal_moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(5):
                            capture_squares = diagonal_moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-4, Move(origin_square, destination, 0, index+6))) # checks will have odd is_check attribute
                    if straight_moveable_squares & all_opp_pieces_bit != 0:
                        for index in range(5):
                            capture_squares = straight_moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append((index-4, Move(origin_square, destination, 0, index+6))) # checks will have odd is_check attribute
            
            # Capturing with pawns that are pinned
            piece_bit = bitboard[6] & diagonal_pins
            if piece_bit != 0: # If we can't move pawns
                pawn_indices = get_set_bit_indices(piece_bit) # The indices of the squares the pawns are in
                for origin_square in pawn_indices: # For position of piece of this type
                    attacking_squares = black_pawn_attacks[origin_square] & diagonal_pins # We get the precomputed moveable squares
                    if attacking_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
                        for index in range(5): # For each of our opponent pieces, except king
                            capture_squares = attacking_squares & bitboard[index] # We get only squares in which opponent pieces are
                            if capture_squares != 0: # If we can capture
                                for destination in get_set_bit_indices(capture_squares):
                                    if destination < 8:
                                        captures.extend([(index, Move(origin_square, destination, 4, index+6)), (index, Move(origin_square, destination, 3, index+6)), 
                                                        (index, Move(origin_square, destination, 2, index+6)), (index, Move(origin_square, destination, 1, index+6))])
                                    else:
                                        captures.append((index, Move(origin_square, destination, 0, index+6))) # checks will have odd is_check attribute

            return [move[1] for move in sorted(captures, key=lambda move: move[0], reverse=True)] # return the moves ordered in terms of the score and make is_check = 0 for all
    
    def non_capture_moves(self):
        '''
        This will be a generator which when checking if move is a check it yields a move with score 1, else 0.
        '''
        bitboard = self.bitboard
        diagonal_pins, straight_pins = self.current_pins
        full_pins = diagonal_pins | straight_pins

        if self.turn: # If whites turn
            all_own_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
            all_opp_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
            all_pieces_bit = all_own_pieces_bit | all_opp_pieces_bit
            
            # Moving pieces that are not pinned

            # Knights
            piece_bit = bitboard[1] & ~full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = knight_moves[origin_square] & ~all_pieces_bit # We get the precomputed moveable squares, note captures are computed on capture_moves().
                    if moveable_squares != 0: # If we can move our piece
                        for destination in get_set_bit_indices(moveable_squares): # get_set_bit_indices is a generator so yielding bellow makes it more efficient
                            yield Move(origin_square, destination, 0, 0)

            # King 
            piece_bit = bitboard[5]
            origin_square = find_least_significant_bit_set(piece_bit) # For position of piece of this type
            moveable_squares = king_moves[origin_square] & ~all_pieces_bit # We get the precomputed moveable squares, note captures are computed on capture_moves().
            if moveable_squares != 0: # If we can move our piece
                if self.wc[0]: # If its whites turn with kingside castling rights (ply_info[-1][0] = wc)
                    if all_pieces_bit & 96 == 0: # If pieces are not blocking
                        if self.king_is_safe(5) and self.king_is_safe(6):
                            yield Move(7, 5, 0, -1) # Make the move as if rook moved (better for move method)

                if self.wc[1]: # If its whites turn with queenside castling rights (ply_info[-1][0] = wc)
                    if all_pieces_bit & 14 == 0: # If pieces are not blocking
                        if self.king_is_safe(2) and self.king_is_safe(3):
                            yield Move(0, 3, 0, -1)
                    
                for destination in get_set_bit_indices(moveable_squares): # get_set_bit_indices is a generator so yielding bellow makes it more efficient
                    if self.king_is_safe(destination):
                        yield Move(origin_square, destination, 0, 0)
                                
            # Pawns
            piece_bit = bitboard[0] & ~full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = white_pawn_moves[origin_square] & ~all_pieces_bit # We get rid of the squares in which our own or opp pieces are
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares): # Promotions
                            if destination > 55:
                                yield Move(origin_square, destination, 4, 0)
                                yield Move(origin_square, destination, 3, 0)
                                yield Move(origin_square, destination, 2, 0)
                                yield Move(origin_square, destination, 1, 0)
                            elif origin_square < 16 and white_pawn_doubles[origin_square] & all_pieces_bit == 0:
                                yield Move(origin_square, destination + 8, 0, 0)
                                yield Move(origin_square, destination, 0, 0)
                            else:
                                yield Move(origin_square, destination, 0, 0)

            # Bishops
            piece_bit = bitboard[2] & ~full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares &= ~ all_pieces_bit
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)

            # Rooks
            piece_bit = bitboard[3] & ~full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares &= ~ all_pieces_bit
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
            
            # Queens
            piece_bit = bitboard[4] & ~full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    diag_moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    diag_moveable_squares &= ~ all_pieces_bit
                    straight_moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    straight_moveable_squares &= ~ all_pieces_bit
                    if straight_moveable_squares != 0:
                        for destination in get_set_bit_indices(straight_moveable_squares):
                            yield Move(origin_square, destination, 0, 0)

                    if diag_moveable_squares != 0:
                        for destination in get_set_bit_indices(diag_moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
            
            # Moving pinned pieces (Note knights cannot be moved if pinned and kings cannot be pinned)

            # Pinned Pawns
            piece_bit = bitboard[0] & straight_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = white_pawn_moves[origin_square] & ~all_pieces_bit & straight_pins # We get rid of the squares in which our own or opp pieces are
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
                            if origin_square < 16 and white_pawn_doubles[origin_square] & all_pieces_bit == 0: # Double advance
                                yield Move(origin_square, destination + 8, 0, 0)

            # Pinned Bishops
            piece_bit = bitboard[2] & diagonal_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares &= ~ all_pieces_bit
                    moveable_squares &= diagonal_pins
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
            # Pinned Rooks
            piece_bit = bitboard[3] & straight_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares &= ~ all_pieces_bit
                    moveable_squares &= straight_pins
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
            
            # Pinned Queens
            piece_bit = bitboard[4] & full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    diag_moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    diag_moveable_squares &= ~ all_pieces_bit
                    diag_moveable_squares &= diagonal_pins
                    straight_moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    straight_moveable_squares &= ~ all_pieces_bit
                    straight_moveable_squares &= straight_pins
                    if straight_moveable_squares != 0:
                        for destination in get_set_bit_indices(straight_moveable_squares):
                            yield Move(origin_square, destination, 0, 0)

                    if diag_moveable_squares != 0:
                        for destination in get_set_bit_indices(diag_moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
        else: # Blacks turn
            all_opp_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
            all_own_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
            all_pieces_bit = all_own_pieces_bit | all_opp_pieces_bit
            
            # Moving pieces that are not pinned

            # Knights
            piece_bit = bitboard[7] & ~full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = knight_moves[origin_square] & ~all_pieces_bit # We get the precomputed moveable squares, note captures are computed on capture_moves().
                    if moveable_squares != 0: # If we can move our piece
                        for destination in get_set_bit_indices(moveable_squares): # get_set_bit_indices is a generator so yielding bellow makes it more efficient
                            yield Move(origin_square, destination, 0, 0)

            # King 
            piece_bit = bitboard[11]
            origin_square = find_least_significant_bit_set(piece_bit) # For position of piece of this type
            moveable_squares = king_moves[origin_square] & ~all_pieces_bit # We get the precomputed moveable squares, note captures are computed on capture_moves().
            if moveable_squares != 0: # If we can move our piece
                if self.bc[0]: # If it's black turn with kingside castling rights (ply_info[-1][1] = bc)
                    if all_pieces_bit & 6917529027641081856 == 0:
                        if self.king_is_safe(61) and self.king_is_safe(62):
                            yield Move(63, 61, 0, -1)
                
                if self.bc[1]: # If its black turn with queenside castling rights (ply_info[-1][1] = bc)
                    if all_pieces_bit & 1008806316530991104 == 0:
                        if self.king_is_safe(59) and self.king_is_safe(58):
                            yield Move(56, 59, 0, -1)
                    
                for destination in get_set_bit_indices(moveable_squares): # get_set_bit_indices is a generator so yielding bellow makes it more efficient
                    if self.king_is_safe(destination):
                        yield Move(origin_square, destination, 0, 0)
                                
            # Pawns
            piece_bit = bitboard[6] & ~full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = black_pawn_moves[origin_square] & ~all_pieces_bit # We get rid of the squares in which our own or opp pieces are
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares): # Promotions
                            if destination < 8:
                                yield Move(origin_square, destination, 4, 0)
                                yield Move(origin_square, destination, 3, 0)
                                yield Move(origin_square, destination, 2, 0)
                                yield Move(origin_square, destination, 1, 0)
                            elif origin_square > 47 and black_pawn_doubles[origin_square] & all_pieces_bit == 0: # Double advance
                                yield Move(origin_square, destination - 8, 0, 0)
                                yield Move(origin_square, destination, 0, 0)
                            else:
                                yield Move(origin_square, destination, 0, 0)

            # Bishops
            piece_bit = bitboard[8] & ~full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares &= ~ all_pieces_bit
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)

            # Rooks
            piece_bit = bitboard[9] & ~full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares &= ~ all_pieces_bit
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
            
            # Queens
            piece_bit = bitboard[10] & ~full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    diag_moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    diag_moveable_squares &= ~ all_pieces_bit
                    straight_moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    straight_moveable_squares &= ~ all_pieces_bit
                    if straight_moveable_squares != 0:
                        for destination in get_set_bit_indices(straight_moveable_squares):
                            yield Move(origin_square, destination, 0, 0)

                    if diag_moveable_squares != 0:
                        for destination in get_set_bit_indices(diag_moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
            
            # Moving pinned pieces (Note knights cannot be moved if pinned and kings cannot be pinned)

            # Pinned Pawns
            piece_bit = bitboard[6] & straight_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = black_pawn_moves[origin_square] & ~all_pieces_bit & straight_pins # We get rid of the squares in which our own or opp pieces are
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
                            if origin_square > 47 and black_pawn_doubles[origin_square] & all_pieces_bit == 0: # Double advance
                                yield Move(origin_square, destination - 8, 0, 0)

            # Pinned Bishops
            piece_bit = bitboard[8] & diagonal_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares &= ~ all_pieces_bit
                    moveable_squares &= diagonal_pins
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
            # Pinned Rooks
            piece_bit = bitboard[9] & straight_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares &= ~ all_pieces_bit
                    moveable_squares &= straight_pins
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
            
            # Pinned Queens
            piece_bit = bitboard[10] & full_pins
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    diag_moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    diag_moveable_squares &= ~ all_pieces_bit
                    diag_moveable_squares &= diagonal_pins
                    straight_moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    straight_moveable_squares &= ~ all_pieces_bit
                    straight_moveable_squares &= straight_pins
                    if straight_moveable_squares != 0:
                        for destination in get_set_bit_indices(straight_moveable_squares):
                            yield Move(origin_square, destination, 0, 0)

                    if diag_moveable_squares != 0:
                        for destination in get_set_bit_indices(diag_moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
    

    def move(self, move):
        '''
        Move piece and switch white and black roles, without rotating the board.
        '''
        self.position_ply_info.append((copy.copy(self.wc), copy.copy(self.bc), copy.copy(self.psquare), copy.copy(self.current_pins), copy.copy(self.current_checks))) # For unmake_move

        if self.turn: # If whites move
            # For captures we take off opponent pieces
            if move.capture == 6 and move.j == self.psquare: # En passant capture (ply_info[-2][2] = last psquare)
                self.bitboard[6] &= ~(1 << (move.j - 8))
            
            elif move.capture != 0 and move.capture != -1: # Any other capture
                self.bitboard[move.capture] &= ~(1 << move.j)
            
            # For all non promotion moves we put our pieces on new squares
            if move.prom == 0: # Any non promotion move
                for indx in range(6):
                    if move.i in get_set_bit_indices(self.bitboard[indx]): # If this is the piece we are moving
                        moving_piece = indx
                        self.bitboard[indx] &= ~(1 << move.i)
                        self.bitboard[indx] |= 1 << move.j

            else: # If we are promoting pawn
                moving_piece = 0
                self.bitboard[0] &= ~(1 << move.i)
                self.bitboard[move.prom] |= 1 << move.j
            
            # Castling (we must also move king)
            if move.capture == -1 and move.i == 0: # White kingside castling
                self.bitboard[5] = 4
                self.wc = [False, False] 
            elif move.capture == -1 and move.i == 7: # White queenside castling
                self.bitboard[5] = 64
                self.wc = [False, False] 

            # Updating castling rights
            elif moving_piece == 5: # If we move king castling rights are lost
                self.wc = [False, False] 
            elif move.i == 0 or move.j == 0: # If we move rook on a1
                self.wc[1] = False
            elif move.i == 7 or move.j == 7: # If we move rook on h1
                self.wc[0] = False 
            elif move.i == 56 or move.j == 56: # If we move rook on a8
                self.bc[1] = False
            elif move.i == 63 or move.j == 63: # If we move rook on h8
                self.bc[0] = False

            # Update psquare if needed
            self.psquare = -1
            if moving_piece == 0 and move.j - move.i == 16: # If we are moving a pawn twice
                self.psquare = move.i + 8 # We store the row to reduce size

        
        else: # Blacks move
            # For captures we take off opponent pieces
            if move.capture == 6 and move.j == self.psquare: # En passant capture
                self.bitboard[0] &= ~(1 << (move.j + 8))
            
            elif move.capture != 0 and move.capture != -1: # Any other capture
                self.bitboard[move.capture-6] &= ~(1 << move.j)

            # For all non promotion moves we put our pieces on new squares
            if move.prom == 0:
                for indx in range(6,12):
                    if move.i in get_set_bit_indices(self.bitboard[indx]): # If this is the piece we are moving
                        moving_piece = indx
                        self.bitboard[indx] &= ~(1 << move.i)
                        self.bitboard[indx] |= 1 << move.j

            else: # If we are promoting pawn
                moving_piece = 6
                self.bitboard[6] &= ~(1 << move.i)
                self.bitboard[move.prom + 6] |= 1 << move.j
            
            
            # Castling (we must also move king)
            if move.capture == -1 and move.i == 56: # Black kingside castling
                self.bitboard[11] = 288230376151711744
                self.bc = [False, False]
            elif move.capture == -1 and move.i == 63: # Black queenside castling
                self.bitboard[11] = 4611686018427387904
                self.bc = [False, False]
            
            # Updating castling rights
            elif moving_piece == 11 and not self.turn: # If we move king castling rights are lost
                self.bc = [False, False]
            elif move.i == 0 or move.j == 0: # If we move rook on a1
                self.wc[1] = False
            elif move.i == 7 or move.j == 7: # If we move rook on h1
                self.wc[0] = False 
            elif move.i == 56 or move.j == 56: # If we move rook on a8
                self.bc[1] = False
            elif move.i == 63 or move.j == 63: # If we move rook on h8
                self.bc[0] = False

            # Update psquare if needed
            self.psquare = -1
            if moving_piece == 6 and move.j - move.i == -16: # If we are moving a pawn twice
                self.psquare = move.j + 8 # We store the row +8 to reduce the size
        
        # Add move ply info
        self.move_ply_info.append((moving_piece, move.capture, move.prom))

        # Update info
        self.current_checks = (0,0,0,0,0,0,0)
        self.current_pins = (0,0)
        self.turn = not self.turn


    def unmake_move(self, move):
        '''
        Takes a move and undoes the move accordingly, updating all position attributes. When the engine transverses the tree of moves it will keep 
        track of some irreversible aspects of the game at each ply. These are (white castling rights, black castling rights, passant square, 
        moving piece, capture index, pins, checks).
        '''
        moving_indx, capture_indx, move_promotion = self.move_ply_info.pop()
        self.wc, self.bc, self.psquare, self.current_pins, self.current_checks = self.position_ply_info.pop() # Update irreversible info

        if self.turn: # Whites turn (Last move was black's)
            # Put back the white captured piece
            if capture_indx == 6 and move.j == self.psquare: # If move was an en passant capture
                self.bitboard[0] |= 1 << move.j + 8

            elif capture_indx != 0 and capture_indx != -1: # If the move was a capture
                self.bitboard[capture_indx-6] |= 1 << move.j

            # Unmove the black moving piece
            if move_promotion == 0:
                self.bitboard[moving_indx] &= ~(1 << move.j)
            else:
                self.bitboard[move_promotion+6] &= ~(1 << move.j)
            self.bitboard[moving_indx] |= 1 << move.i

            # Undoing castling, we must also move the king (the part above takes care of the rook)
            if capture_indx == -1:
                self.bitboard[11] = 1152921504606846976
                
        else: # Blacks turn (Last move was white's)
            # Put back the black captured piece
            if capture_indx == 6 and move.j == self.psquare: # If move was an en passant capture
                self.bitboard[6] |= 1 << move.j - 8  

            elif capture_indx != 0 and capture_indx != -1: # If the move was a capture
                self.bitboard[capture_indx] |= 1 << move.j

            # Unmove the white moving piece
            if move_promotion == 0:
                self.bitboard[moving_indx] &= ~(1 << move.j)
            else:
                self.bitboard[move_promotion] &= ~(1 << move.j)

            self.bitboard[moving_indx] |= 1 << move.i

            # Undoing castling, we must also move the king (the part above takes care of the rook)
            if capture_indx == -1:
                self.bitboard[5] = 16
        
        self.turn = not self.turn


######################################################
# Simple evaluation function (CHECK THE POINTS PER SQUARE ARE RELIABLE)
#####################################################3
# First elements correspond to h8 and last to a1
# White Pawns (Encouraging center control and advancement)
white_pawns = np.array([
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 5, 5, 5, 5, 5, 5, 5,
    1, 1, 2, 4, 4, 2, 1, 1,
    1, 1, 1, 3, 3, 1, 1, 1,
    1, 1, 1, 3, 3, 1, 1, 1,
    1, 1, 1, 2, 2, 1, 1, 1,
    5, 5, 1, 1, 1, 1, 1, 1,
    0, 0, 0, 0, 0, 0, 0, 0
])

# White Knights (Prioritizing central and advanced positions)
white_knights = np.array([
    1, 2, 3, 3, 3, 3, 2, 1,
    2, 3, 4, 4, 4, 4, 3, 2,
    3, 4, 5, 5, 5, 5, 4, 3,
    3, 4, 5, 5, 5, 5, 4, 3,
    3, 4, 5, 5, 5, 5, 4, 3,
    3, 4, 5, 5, 5, 5, 4, 3,
    2, 3, 4, 4, 4, 4, 3, 2,
    1, 2, 3, 3, 3, 3, 2, 1
])

# White Bishops (Valuing central and diagonal control)
white_bishops = np.array([
    2, 3, 3, 3, 3, 3, 3, 2,
    3, 4, 4, 4, 4, 4, 4, 3,
    3, 4, 5, 5, 5, 5, 4, 3,
    3, 4, 5, 5, 5, 5, 4, 3,
    3, 4, 5, 5, 5, 5, 4, 3,
    3, 4, 5, 5, 5, 5, 4, 3,
    3, 4, 4, 4, 4, 4, 4, 3,
    2, 3, 3, 3, 3, 3, 3, 2
])

# White Rooks (Valuing open files and back rank protection)
white_rooks = np.array([
    1, 1, 1, 2, 2, 1, 1, 1,
    2, 2, 2, 2, 2, 2, 2, 2,
    1, 2, 2, 2, 2, 2, 2, 1,
    1, 2, 2, 2, 2, 2, 2, 1,
    1, 2, 2, 2, 2, 2, 2, 1,
    1, 2, 2, 2, 2, 2, 2, 1,
    1, 2, 2, 2, 2, 2, 2, 1, 
    1, 1, 2, 4, 4, 3, 1, 1
    ])

# White Queen (General value across the board with slight central preference)
white_queen = np.array([
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1
])

# White King (Early game positioning, safer in the corners/castled)
white_king = np.array([
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    4, 5, 5, 3, 3, 5, 5, 4
])

# These tables can be mirrored for black pieces by reversing the rows
black_pawns = np.flipud(white_pawns)
black_knights = np.flipud(white_knights)
black_bishops = np.flipud(white_bishops)
black_rooks = np.flipud(white_rooks)
black_queen = np.flipud(white_queen)
black_king = np.flipud(white_king)

points = (white_pawns, white_knights, white_bishops, white_rooks, white_queen, white_king, black_pawns, black_knights, black_bishops, black_rooks, black_queen, black_king)

def evaluation_function_white(bitposition):
    material_value = (20, 40, 40, 50, 90, 100,
                      -20, -40, -40, -50, -90, -100)
    total_eval = 0
    for i, bit in enumerate(bitposition.bitboard):
        if i < 6:
            total_eval += sum(material_value[i]*bit_to_numpy_array(bit)+bit_to_numpy_array(bit)*points[i])
        else:
            total_eval += sum(material_value[i]*bit_to_numpy_array(bit)-bit_to_numpy_array(bit)*points[i])
    return total_eval

def evaluation_function_black(bitposition):
    material_value = (-20, -40, -40, -50, -90, -100,
                      20, 40, 40, 50, 90, 100)
    total_eval = 0
    for i, bit in enumerate(bitposition.bitboard):
        if i < 6:
            total_eval += sum(material_value[i]*bit_to_numpy_array(bit)-bit_to_numpy_array(bit)*points[i])
        else:
            total_eval += sum(material_value[i]*bit_to_numpy_array(bit)+bit_to_numpy_array(bit)*points[i])
    return total_eval


######################################################
# Zobrist Hashing
######################################################


def position_to_zobrist_key(bitposition):
    key = 0
    for i, bit in enumerate(bitposition.bitboard):
        array = bit_to_numpy_array(bit) * zobrist_numbers_pieces[i]
        for element in array:
            if element != 0:
                key ^= element
    if not bitposition.turn: # If black is moving
        key ^= black_to_move_zobrist_number
    # Castling key (we first get a 16 bit integer representing the castling rights)
    castling_bit = bitposition.wc[0] << 3
    castling_bit |= bitposition.wc[1] << 2
    castling_bit |= bitposition.bc[0] << 1
    castling_bit |= bitposition.bc[1] << 0
    key ^= castling_rights_zobrist_numbers[castling_bit]
    # Passant key
    key ^= passant_squares_zobrist_numbers[bitposition.passant_square]
    return key



######################################################
# Search
######################################################

import time
import itertools

class Engine:
    '''
    In this engine a good evaluation for us will be positive and a good evaluation for opponent will be negative.
    '''
    def __init__(self, evaluation_func):
        self.evaluation_func = evaluation_func
        self.current_depth = 1
        self.last_best_move = None
        self.hash_table = {}


    def alpha_beta(self, position, depth, alpha, beta, our_turn):
        # Captures
        '''
        if position.three_fold():  # Repetitions
            return 0, 0
        '''
        
        is_check = position.is_check()

        # Quiesence search (Only captures)
        if depth <= 0 and is_check:
            capture_moves = position.in_check_captures()
            non_capture_moves = []
        elif depth <= 0 and not is_check:
            capture_moves = position.capture_moves()
            non_capture_moves = []
        # Normal search
        elif is_check: # If we are in check
            capture_moves = position.in_check_captures()
            non_capture_moves = position.in_check_moves()
        else:
            capture_moves = position.capture_moves()
            non_capture_moves = position.non_capture_moves()
        
        if depth > 0:
            value1 = -10004  # This is the best evaluation for us in the child_values (we start at the worst possible evaluation)
            value2 = 10004 # This is the best evaluation for opponent in the child_values (we start at the worst possible evaluation)
        elif our_turn: # If we are in quiescence, we have a baseline evaluation as if no captures happened
            value1 = self.evaluation_func(position)
        else:
            value2 = self.evaluation_func(position)

        best_move = None
        if depth == self.current_depth and self.last_best_move != None: # If we are starting an alpha beta search and we have already a previous best we will start with the previous best
            capture_moves.insert(0, self.last_best_move)

        if our_turn:  
            # If we have to move, we want to maximize. This is ensured because the evaluation function takes into account if engine is 
            # playing as white or not.
            for move in itertools.chain(capture_moves, non_capture_moves):
                position.move(move)
                child_value = self.alpha_beta(position, depth - 1, alpha, beta, False)[0]
                if child_value > value1:
                    # If we can improve the best value, then we have found a better move in the child values
                    value1 = child_value
                    best_move = move
                position.unmake_move(move)
                if value1 >= beta:
                    # If our best move is better than the best in another set of moves that lead from a different 
                    # move from opponent, then opponent will choose the other move. So theres no need to calculate in this set
                    # of child values anymore.
                    break 
                alpha = max(alpha, value1) 

        else:  # If opponent has to move
            for move in itertools.chain(capture_moves, non_capture_moves):
                position.move(move)
                child_value = self.alpha_beta(position, depth - 1, alpha, beta, True)[0]
                if child_value < value2:
                    value2 = child_value
                    best_move = move
                position.unmake_move(move) 
                if alpha >= value2:
                    # If opponent's best move is better than the best in another set of moves that lead from a different 
                    # move (parent2) from us, then we will choose the other move (parent2). So there's no need to calculate in
                    # this set of child moves any more.
                    break             
                beta = min(beta, value2)
        # If we have reached quisence search and there are no captures

        if best_move == None and depth <= 0:
            return self.evaluation_func(position), 0
        
        # If we reach a position where game has ended

        if best_move == None and not is_check:  # Stalemate (There are no captures or non captures and no checks)
            return 0, 0

        if best_move == None and our_turn and is_check:  # Checkmate against us
            return -10003, 0

        if best_move == None and not our_turn and is_check:  # Checkmate against opponent
            return 10003, 0

        # If there has been an alpha/beta break, then value1 and value2 are going to be telling the player that moved before,
        # that the move was worse than a previously calculated one (in the same depth).

        if our_turn:
            x = value1
        else:
            x = value2

        return (x, best_move)

    def Search(self, position, time_left):
        # alpha is the current best evaluation for white, it will start at -1000
        # beta is the current best evaluation for black, it will start at +1000
        start_time = time.time()
        time_for_move = self.TimeManager(position, time_left)
        best_move = None
        alpha = -10005
        beta = 10005
        for depth in range(1,15):
            self.current_depth = depth
            best_value, best_move = self.alpha_beta(position, depth, alpha, beta, our_turn = True)
            self.last_best_move = best_move
            if time.time() - start_time > time_left:
                break

        return ["Time taken:", time.time() - start_time, "seconds", "Best move: ", self.last_best_move, "Evaluation: ", best_value, 'Depth:', depth]

    def TimeManager(self, position, time_left):
        return 5
