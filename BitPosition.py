import numpy as np
import json

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


####################################
# Pre-computed crawler tables 
####################################



# Precomputed move tables
knight_moves = (132096, 329728, 659712, 1319424, 2638848, 5277696, 10489856, 4202496, 33816580, 84410376, 168886289, 337772578, 675545156, 1351090312, 2685403152, 1075839008, 8657044482, 21609056261, 43234889994, 86469779988, 172939559976, 345879119952, 687463207072, 275414786112, 2216203387392, 5531918402816, 11068131838464, 22136263676928, 44272527353856, 88545054707712, 175990581010432, 70506185244672, 567348067172352, 1416171111120896, 2833441750646784, 5666883501293568, 11333767002587136, 22667534005174272, 45053588738670592, 18049583422636032, 145241105196122112, 362539804446949376, 725361088165576704, 1450722176331153408, 2901444352662306816, 5802888705324613632, 11533718717099671552, 4620693356194824192, 288234782788157440, 576469569871282176, 1224997833292120064, 2449995666584240128, 4899991333168480256, 9799982666336960512, 1152939783987658752, 2305878468463689728, 1128098930098176, 2257297371824128, 4796069720358912, 9592139440717824, 19184278881435648, 38368557762871296, 4679521487814656, 9077567998918656)
king_moves = (770, 1797, 3594, 7188, 14376, 28752, 57504, 49216, 197123, 460039, 920078, 1840156, 3680312, 7360624, 14721248, 12599488, 50463488, 117769984, 235539968, 471079936, 942159872, 1884319744, 3768639488, 3225468928, 12918652928, 30149115904, 60298231808, 120596463616, 241192927232, 482385854464, 964771708928, 825720045568, 3307175149568, 7718173671424, 15436347342848, 30872694685696, 61745389371392, 123490778742784, 246981557485568, 211384331665408, 846636838289408, 1975852459884544, 3951704919769088, 7903409839538176, 15806819679076352, 31613639358152704, 63227278716305408, 54114388906344448, 216739030602088448, 505818229730443264, 1011636459460886528, 2023272918921773056, 4046545837843546112, 8093091675687092224, 16186183351374184448, 13853283560024178688, 144959613005987840, 362258295026614272, 724516590053228544, 1449033180106457088, 2898066360212914176, 5796132720425828352, 11592265440851656704, 4665729213955833856)
white_pawn_moves = (256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 16842752, 33685504, 67371008, 134742016, 269484032, 538968064, 1077936128, 2155872256, 16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648, 4294967296, 8589934592, 17179869184, 34359738368, 68719476736, 137438953472, 274877906944, 549755813888, 1099511627776, 2199023255552, 4398046511104, 8796093022208, 17592186044416, 35184372088832, 70368744177664, 140737488355328, 281474976710656, 562949953421312, 1125899906842624, 2251799813685248, 4503599627370496, 9007199254740992, 18014398509481984, 36028797018963968, 72057594037927936, 144115188075855872, 288230376151711744, 576460752303423488, 1152921504606846976, 2305843009213693952, 4611686018427387904, 9223372036854775808, 0, 0, 0, 0, 0, 0, 0, 0)
white_pawn_attacks = (512, 1280, 2560, 5120, 10240, 20480, 40960, 16384, 131072, 327680, 655360, 1310720, 2621440, 5242880, 10485760, 4194304, 33554432, 83886080, 167772160, 335544320, 671088640, 1342177280, 2684354560, 1073741824, 8589934592, 21474836480, 42949672960, 85899345920, 171798691840, 343597383680, 687194767360, 274877906944, 2199023255552, 5497558138880, 10995116277760, 21990232555520, 43980465111040, 87960930222080, 175921860444160, 70368744177664, 562949953421312, 1407374883553280, 2814749767106560, 5629499534213120, 11258999068426240, 22517998136852480, 45035996273704960, 18014398509481984, 144115188075855872, 360287970189639680, 720575940379279360, 1441151880758558720, 2882303761517117440, 5764607523034234880, 11529215046068469760, 4611686018427387904, 0, 0, 0, 0, 0, 0, 0, 0)
black_pawn_moves = (0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648, 4294967296, 8589934592, 17179869184, 34359738368, 68719476736, 137438953472, 274877906944, 549755813888, 1103806595072, 2207613190144, 4415226380288, 8830452760576, 17660905521152, 35321811042304, 70643622084608, 141287244169216, 281474976710656, 562949953421312, 1125899906842624, 2251799813685248, 4503599627370496, 9007199254740992, 18014398509481984, 36028797018963968)
black_pawn_attacks = (0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 10, 20, 40, 80, 160, 64, 512, 1280, 2560, 5120, 10240, 20480, 40960, 16384, 131072, 327680, 655360, 1310720, 2621440, 5242880, 10485760, 4194304, 33554432, 83886080, 167772160, 335544320, 671088640, 1342177280, 2684354560, 1073741824, 8589934592, 21474836480, 42949672960, 85899345920, 171798691840, 343597383680, 687194767360, 274877906944, 2199023255552, 5497558138880, 10995116277760, 21990232555520, 43980465111040, 87960930222080, 175921860444160, 70368744177664, 562949953421312, 1407374883553280, 2814749767106560, 5629499534213120, 11258999068426240, 22517998136852480, 45035996273704960, 18014398509481984)

board = [ 'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R',
         'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
         '0', '0', '0', '0', '0', '0', '0', '0',
         '0', '0', '0', '0', '0', '0', '0', '0',
         '0', '0', '0', '0', '0', '0', '0', '0',
         '0', '0', '0', '0', '0', '0', '0', '0',
         'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
         'r', 'n', 'b', 'q', 'k', 'b', 'n', 'k' ]


####################################
# Pre-computed slider tables 
####################################
# Number of squares in direction to move from all squares
rook_unfull_rays = (282578800148862, 565157600297596, 1130315200595066, 2260630401190006, 4521260802379886, 9042521604759646, 18085043209519166, 36170086419038334, 282578800180736, 565157600328704, 1130315200625152, 2260630401218048, 4521260802403840, 9042521604775424, 18085043209518592, 36170086419037696, 282578808340736, 565157608292864, 1130315208328192, 2260630408398848, 4521260808540160, 9042521608822784, 18085043209388032, 36170086418907136, 282580897300736, 565159647117824, 1130317180306432, 2260632246683648, 4521262379438080, 9042522644946944, 18085043175964672, 36170086385483776, 283115671060736, 565681586307584, 1130822006735872, 2261102847592448, 4521664529305600, 9042787892731904, 18085034619584512, 36170077829103616, 420017753620736, 699298018886144, 1260057572672512, 2381576680245248, 4624614895390720, 9110691325681664, 18082844186263552, 36167887395782656, 35466950888980736, 34905104758997504, 34344362452452352, 33222877839362048, 30979908613181440, 26493970160820224, 17522093256097792, 35607136465616896, 9079539427579068672, 8935706818303361536, 8792156787827803136, 8505056726876686336, 7930856604974452736, 6782456361169985536, 4485655873561051136, 9115426935197958144)
bishop_unfull_rays = (18049651735527936, 70506452091904, 275415828992, 1075975168, 38021120, 8657588224, 2216338399232, 567382630219776, 9024825867763712, 18049651735527424, 70506452221952, 275449643008, 9733406720, 2216342585344, 567382630203392, 1134765260406784, 4512412933816832, 9024825867633664, 18049651768822272, 70515108615168, 2491752130560, 567383701868544, 1134765256220672, 2269530512441344, 2256206450263040, 4512412900526080, 9024834391117824, 18051867805491712, 637888545440768, 1135039602493440, 2269529440784384, 4539058881568768, 1128098963916800, 2256197927833600, 4514594912477184, 9592139778506752, 19184279556981248, 2339762086609920, 4538784537380864, 9077569074761728, 562958610993152, 1125917221986304, 2814792987328512, 5629586008178688, 11259172008099840, 22518341868716544, 9007336962655232, 18014673925310464, 2216338399232, 4432676798464, 11064376819712, 22137335185408, 44272556441600, 87995357200384, 35253226045952, 70506452091904, 567382630219776, 1134765260406784, 2832480465846272, 5667157807464448, 11333774449049600, 22526811443298304, 9024825867763712, 18049651735527936)
queen_unfull_rays = (18332230535676798, 635664052389500, 1130590616424058, 2260631477165174, 4521260840401006, 9042530262347870, 18087259547918398, 36737469049258110, 9307404667944448, 18614809335856128, 1200821652847104, 2260905850861056, 4521270535810560, 9044737947360768, 18652425839721984, 37304851679444480, 4794991742157568, 9589983475926528, 19179966977150464, 2331145517014016, 4523752560670720, 9609905310691328, 19219808465608704, 38439616931348480, 2538787347563776, 5077572547643904, 10155151571424256, 20312500052175360, 5159150924878848, 10177562247440384, 20354572616749056, 40709145267052544, 1411214634977536, 2821879514141184, 5645416919213056, 11853242626099200, 23705944086286848, 11382549979341824, 22623819156965376, 45247646903865344, 982976364613888, 1825215240872448, 4074850560001024, 8011162688423936, 15883786903490560, 31629033194398208, 27090181148918784, 54182561321093120, 35469167227379968, 34909537435795968, 34355426829272064, 33245015174547456, 31024181169623040, 26581965518020608, 17557346482143744, 35677642917708800, 9080106810209288448, 8936841583563768320, 8794989268293649408, 8510723884684150784, 7942190379423502336, 6804983172613283840, 4494680699428814848, 9133476586933486080)
rook_full_rays = (72340172838076926, 144680345676153597, 289360691352306939, 578721382704613623, 1157442765409226991, 2314885530818453727, 4629771061636907199, 9259542123273814143, 72340172838141441, 144680345676217602, 289360691352369924, 578721382704674568, 1157442765409283856, 2314885530818502432, 4629771061636939584, 9259542123273813888, 72340172854657281, 144680345692602882, 289360691368494084, 578721382720276488, 1157442765423841296, 2314885530830970912, 4629771061645230144, 9259542123273748608, 72340177082712321, 144680349887234562, 289360695496279044, 578721386714368008, 1157442769150545936, 2314885534022901792, 4629771063767613504, 9259542123257036928, 72341259464802561, 144681423712944642, 289361752209228804, 578722409201797128, 1157443723186933776, 2314886351157207072, 4629771607097753664, 9259542118978846848, 72618349279904001, 144956323094725122, 289632270724367364, 578984165983651848, 1157687956502220816, 2315095537539358752, 4629910699613634624, 9259541023762186368, 143553341945872641, 215330564830528002, 358885010599838724, 645993902138460168, 1220211685215703056, 2368647251370188832, 4665518383679160384, 9259260648297103488, 18302911464433844481, 18231136449196065282, 18087586418720506884, 17800486357769390088, 17226286235867156496, 16077885992062689312, 13781085504453754944, 9187484529235886208)
bishop_full_rays = (9241421688590303744, 36099303471056128, 141012904249856, 550848566272, 6480472064, 1108177604608, 283691315142656, 72624976668147712, 4620710844295151618, 9241421688590368773, 36099303487963146, 141017232965652, 1659000848424, 283693466779728, 72624976676520096, 145249953336262720, 2310355422147510788, 4620710844311799048, 9241421692918565393, 36100411639206946, 424704217196612, 72625527495610504, 145249955479592976, 290499906664153120, 1155177711057110024, 2310355426409252880, 4620711952330133792, 9241705379636978241, 108724279602332802, 145390965166737412, 290500455356698632, 580999811184992272, 577588851267340304, 1155178802063085600, 2310639079102947392, 4693335752243822976, 9386671504487645697, 326598935265674242, 581140276476643332, 1161999073681608712, 288793334762704928, 577868148797087808, 1227793891648880768, 2455587783297826816, 4911175566595588352, 9822351133174399489, 1197958188344280066, 2323857683139004420, 144117404414255168, 360293502378066048, 720587009051099136, 1441174018118909952, 2882348036221108224, 5764696068147249408, 11529391036782871041, 4611756524879479810, 567382630219904, 1416240237150208, 2833579985862656, 5667164249915392, 11334324221640704, 22667548931719168, 45053622886727936, 18049651735527937)
queen_full_rays = (9313761861428380670, 180779649147209725, 289501704256556795, 578721933553179895, 1157442771889699055, 2314886638996058335, 4630054752952049855, 9332167099941961855, 4693051017133293059, 9386102034266586375, 325459994840333070, 578862399937640220, 1157444424410132280, 2315169224285282160, 4702396038313459680, 9404792076610076608, 2382695595002168069, 4765391190004401930, 9530782384287059477, 614821794359483434, 1157867469641037908, 2387511058326581416, 4775021017124823120, 9550042029937901728, 1227517888139822345, 2455035776296487442, 4910072647826412836, 9820426766351346249, 1266167048752878738, 2460276499189639204, 4920271519124312136, 9840541934442029200, 649930110732142865, 1299860225776030242, 2600000831312176196, 5272058161445620104, 10544115227674579473, 2641485286422881314, 5210911883574396996, 10421541192660455560, 361411684042608929, 722824471891812930, 1517426162373248132, 3034571949281478664, 6068863523097809168, 12137446670713758241, 5827868887957914690, 11583398706901190788, 287670746360127809, 575624067208594050, 1079472019650937860, 2087167920257370120, 4102559721436811280, 8133343319517438240, 16194909420462031425, 13871017173176583298, 18303478847064064385, 18232552689433215490, 18090419998706369540, 17806153522019305480, 17237620560088797200, 16100553540994408480, 13826139127340482880, 9205534180971414145)

# Combining into a tuple of tuples
precomputed_move_tables = (white_pawn_moves, knight_moves, bishop_full_rays, rook_full_rays, queen_full_rays, king_moves, white_pawn_attacks, black_pawn_attacks, black_pawn_moves)
slider_unfull_rays = (bishop_unfull_rays, rook_unfull_rays, queen_unfull_rays)


# Precomputed bishop and rook moves without magic numbers
from utils import generate_bit_combinations, get_valid_piece_moves_including_captures

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

passant_bitboards = {-1: 0, 
                     0 : 65536, 1 : 131072, 2 : 262144, 3 : 524288, 4 : 1048576, 5 : 2097152, 6 : 4194304, 7: 8388608, 
                     8 : 1099511627776, 9 : 2199023255552, 10 : 4398046511104, 11 : 8796093022208, 12 : 17592186044416, 13 : 35184372088832, 14 : 70368744177664, 15 : 140737488355328}

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
from utils import get_set_bit_indices, find_least_significant_bit_set, has_one_one
Move = namedtuple("Move", "i j prom capture")  # So to define a move we must do Move(square, destination_square, promotion(maybe use array index), move_score)
            
             
            
class BitPosition:
    def __init__(self, bitboard, psquare, wc, bc, turn):
        self.bitboard = bitboard  # list of 64-bit integers: w_pawns, w_knights, w_bishops, w_rooks, w_queens, w_king, ...
        self.psquare = psquare  # An integer representing the square that can be captured using en passant.
        # It will be -1 if the last move wasn't a double pawn move.
        # I will change the passant variable every time a double pawn move is made in
        # the move method.
        self.wc = wc
        self.bc = bc  # The castling rights, these will be lists of two Boolean variables. The first element
        # of the list represents kingside castle, the second queenside castle. They only check
        # if the king or rook has already moved (to check if there are in between checks we do
        # it in gen_moves method).
        self.turn = turn  # True if white's turn, False if black
        self.pins = 0

    def get_pins_bits(self):
        '''
        Get a bitboard of the pinned squares, these are squares containg pinned piece and the ray.
        '''
        bitboard = self.bitboard
        pins = []
        king_position = find_least_significant_bit_set(bitboard[5])
        all_own_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
        all_opp_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]

        # Bishop pins
        if bitboard[8] != 0:
            for square in get_set_bit_indices(bitboard[8]):
                if bishop_full_rays[square] & bitboard[5] != 0:
                    bishop_ray = ((long_precomputed_bishop_table[square][all_opp_pieces_bit & bishop_unfull_rays[square]]|bitboard[8]) & long_precomputed_bishop_table[king_position][all_opp_pieces_bit & bishop_unfull_rays[king_position]])
                    if has_one_one(bishop_ray & all_own_pieces_bit):
                        pins.append(bishop_ray)
        
        # Rook pins
        if bitboard[9] != 0:
            for square in get_set_bit_indices(bitboard[9]):
                if rook_full_rays[square] & bitboard[5] != 0:
                    rook_ray = ((long_precomputed_rook_table[square][all_opp_pieces_bit & rook_unfull_rays[square]]|bitboard[9]) & long_precomputed_rook_table[king_position][all_opp_pieces_bit & rook_unfull_rays[king_position]]) 
                    if has_one_one(rook_ray & all_own_pieces_bit):
                        pins.append(rook_ray)
        
        # Queen pins
        if bitboard[10] != 0:
            for square in get_set_bit_indices(bitboard[10]):
                if bishop_full_rays[square] & bitboard[5] != 0:
                    bishop_ray = ((long_precomputed_bishop_table[square][all_opp_pieces_bit & bishop_unfull_rays[square]]|bitboard[10]) & long_precomputed_bishop_table[king_position][all_opp_pieces_bit & bishop_unfull_rays[king_position]]) 
                    if has_one_one(bishop_ray & all_own_pieces_bit):
                        pins.append(bishop_ray)
                if rook_full_rays[square] & bitboard[5] != 0:
                    rook_ray = ((long_precomputed_rook_table[square][all_opp_pieces_bit & rook_unfull_rays[square]]|bitboard[10]) & long_precomputed_rook_table[king_position][all_opp_pieces_bit & rook_unfull_rays[king_position]]) 
                    if has_one_one(rook_ray & all_own_pieces_bit):
                        pins.append(rook_ray)

        self.pins = pins
    
    
    def king_is_safe(self, destination):
        '''
        See if the king is in check or not (from kings position). For when moving the king.
        '''
        bitboard = self.bitboard
        all_own_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
        all_opp_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
        
        # Pawns
        if bitboard[6] != 0: # For pawns we have to be carefull because they move upwards or downwards depending on whose turn it is
            if self.turn: # White's turn
                attacking_squares = precomputed_move_tables[6][destination]
                if attacking_squares & bitboard[6] != 0:
                    return False
            else: # Black's turn
                attacking_squares = precomputed_move_tables[7][destination]
                if attacking_squares & bitboard[6] != 0:
                    return False

        # Knights
        if bitboard[7] != 0:
            moveable_squares = precomputed_move_tables[1][destination]
            if moveable_squares & bitboard[7] != 0: # If there is a knight giving check
                return False
        # Bishops
        if bitboard[8] != 0:
            moveable_squares = long_precomputed_bishop_table[destination][bishop_unfull_rays[destination] & (all_own_pieces_bit | all_opp_pieces_bit)]
            if moveable_squares & bitboard[8] != 0: # If there is a bishop giving check
                return False
        # Rooks
        if bitboard[9] != 0:
            moveable_squares = long_precomputed_rook_table[destination][rook_unfull_rays[destination] & (all_own_pieces_bit | all_opp_pieces_bit)]
            if moveable_squares & bitboard[9] != 0: # If there is a rook giving check
                return False
        # Queens
        if bitboard[10] != 0:
            straight_moveable_squares = long_precomputed_rook_table[destination][rook_unfull_rays[destination] & (all_own_pieces_bit | all_opp_pieces_bit)]
            diag_moveable_squares = long_precomputed_bishop_table[destination][bishop_unfull_rays[destination] & (all_own_pieces_bit | all_opp_pieces_bit)] 
            if straight_moveable_squares & bitboard[10] != 0: # If there is a queen giving check horizontally or vertically
                return False
            if diag_moveable_squares & bitboard[10] != 0: # If there is a queen giving check diagonally
                return False
        return True
    
    def get_checks(self):
        '''
        Count number of checks and if any slider checks return the bit corresponding to the ray of the slider giving check (To block it later).
        Since after making a check we store in the bitposition we have done so. Hence position has in_check attribute = True.
        We are going to check for checks more efficiently from the kings position and assuming it can move as any piece.
        '''
        bitboard = self.bitboard
        king_position = find_least_significant_bit_set(bitboard[5])
        all_own_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
        all_opp_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
        checks = 0 # Positions of pieces giving checks (one bitboard)
        rays = 0 # Rays of sliders giving checks
        num_checks = 0 # Number of checks
        
        # Pawns (Note we can only give check with one pawn at a time)
        if bitboard[6] != 0: # For pawns we have to be carefull because they move upwards or downwards depending on whose turn it is
            if self.turn: # White's turn
                attacking_squares = precomputed_move_tables[7][king_position]
                if attacking_squares & bitboard[6] != 0:
                    checks |= attacking_squares & bitboard[6]
                    num_checks += 1
            else: # Black's turn
                attacking_squares = precomputed_move_tables[6][king_position]
                if attacking_squares & bitboard[6] != 0:
                    checks |= attacking_squares & bitboard[6]
                    num_checks += 1

        # Knights (Note we can only give check with one knight at a time)
        if bitboard[7] != 0:
            moveable_squares = precomputed_move_tables[1][king_position]
            if moveable_squares & bitboard[7] != 0: # If there is a knight giving check
                checks |= moveable_squares & bitboard[7]
                num_checks += 1

        all_pieces_bit = all_own_pieces_bit | all_opp_pieces_bit
        # Bishops (Note we can only give check with one bishop at a time)
        if bitboard[8] != 0:
            moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_pieces_bit)]
            if moveable_squares & bitboard[8] != 0: # If there is a bishop giving check
                for bishop_position in get_set_bit_indices(bitboard[8]):
                    rays = moveable_squares & long_precomputed_bishop_table[bishop_position][bishop_unfull_rays[bishop_position] & (all_pieces_bit)]
                    checks |= moveable_squares & bitboard[8]
                num_checks += 1
        # Rooks (Note we can only give check with one rook at a time)
        if bitboard[9] != 0:
            moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_pieces_bit)]
            if moveable_squares & bitboard[9] != 0: # If there is a rook giving check
                for rook_position in get_set_bit_indices(bitboard[9]):
                    rays = moveable_squares & long_precomputed_rook_table[rook_position][rook_unfull_rays[rook_position] & (all_pieces_bit)]
                    checks |= moveable_squares & bitboard[9]
                num_checks += 1
        # Queens (Note we can give only give check with one queen at a time)
        if bitboard[10] != 0:
            straight_moveable_squares = long_precomputed_rook_table[king_position][rook_unfull_rays[king_position] & (all_pieces_bit)]
            diag_moveable_squares = long_precomputed_bishop_table[king_position][bishop_unfull_rays[king_position] & (all_pieces_bit)] 
            if straight_moveable_squares & bitboard[10] != 0: # If there is a queen giving check horizontally or vertically
                for queen_position in get_set_bit_indices(bitboard[10]):
                    rays = straight_moveable_squares & long_precomputed_rook_table[queen_position][rook_unfull_rays[queen_position] & (all_pieces_bit)]
                    checks |= straight_moveable_squares & bitboard[10]
                num_checks += 1
            if diag_moveable_squares & bitboard[10] != 0: # If there is a queen giving check diagonally
                for queen_position in get_set_bit_indices(bitboard[10]):
                    rays = diag_moveable_squares & long_precomputed_bishop_table[queen_position][bishop_unfull_rays[queen_position] & (all_pieces_bit)]
                    checks |= diag_moveable_squares & bitboard[10]
                num_checks += 1
        return checks, rays, num_checks

    def in_check_moves(self):
        '''
        We are going to check for checks more efficiently from the kings position and assuming it can move as any piece.
        This will yield the moves to reduce computational time.
        '''
        bitboard = self.bitboard
        all_own_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
        checks, rays, num_checks = self.get_checks()
        

        # We go piece by piece yielding capturing and blocking moves
        # Capturing with King
        piece_bit = bitboard[5]
        origin_square = find_least_significant_bit_set(piece_bit) # We get the indices of the squares pieces of this type are in
        capture_check_squares = precomputed_move_tables[5][origin_square] & checks # We get the precomputed moveable squares
        if capture_check_squares != 0: # If we can capture
            for destination in get_set_bit_indices(capture_check_squares):
                if self.king_is_safe(destination):
                    yield Move(origin_square, destination, 0, 0)

        if num_checks == 1: # We can only capture (with a piece that is not the king) or block if there is only one check
            # Capturing and blocking with Pawns
            piece_bit = bitboard[0]
            if piece_bit != 0: # If we can't move pawns
                pawn_indices = get_set_bit_indices(piece_bit) # The indices of the squares the pawns are in
                for origin_square in pawn_indices: # For position of piece of this type
                    if self.turn: 
                        capture_check_squares = precomputed_move_tables[6][origin_square] & checks # We get the precomputed moveable squares
                    else:
                        capture_check_squares = precomputed_move_tables[7][origin_square] & checks # We get the precomputed moveable squares
                    if capture_check_squares != 0: # If we can capture pieces giving check
                        for destination in get_set_bit_indices(capture_check_squares):
                            yield Move(origin_square, destination, 0, 0)
                    if self.turn: 
                        moveable_check_squares = precomputed_move_tables[0][origin_square] & rays # We get the precomputed moveable squares
                    else:
                        moveable_check_squares = precomputed_move_tables[8][origin_square] & rays # We get the precomputed moveable squares
                    if moveable_check_squares != 0: # If we can capture pieces giving check
                        for destination in get_set_bit_indices(moveable_check_squares):
                            yield Move(origin_square, destination, 0, 0) 

            # Capturing and blocking with knights
            piece_bit = bitboard[1]
            if piece_bit != 0: # If we have no pieces of the current type
                bit_indices = get_set_bit_indices(piece_bit) # We get the indices of the squares pieces of this type are in
                for origin_square in bit_indices: # For position of piece of this type
                    capture_block_check_squares = precomputed_move_tables[1][origin_square] & (checks | rays) # We get the precomputed moveable squares
                    if capture_block_check_squares != 0: # If we can capture
                        for destination in get_set_bit_indices(capture_block_check_squares):
                            yield Move(origin_square, destination, 0, 0) 
            
            all_pieces_bit = all_own_pieces_bit | bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]

            # Capturing with Rooks
            piece_bit = bitboard[3]
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    capture_block_check_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)] & (checks | rays)
                    if capture_block_check_squares != 0:
                        destination_bits = get_set_bit_indices(capture_block_check_squares)
                        for destination in destination_bits:
                            yield Move(origin_square, destination, 0, 0)

            # Capturing with Bishops
            piece_bit = bitboard[2]
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    capture_block_check_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)] & (checks | rays)
                    if capture_block_check_squares != 0:
                        destination_bits = get_set_bit_indices(capture_block_check_squares)
                        for destination in destination_bits:
                            yield Move(origin_square, destination, 0, 0) 
            
            # Capturing with Queens
            piece_bit = bitboard[4]
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    capture_block_check_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    capture_block_check_squares |= long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    capture_block_check_squares &= (checks | rays)
                    if capture_block_check_squares != 0:
                        destination_bits = get_set_bit_indices(capture_block_check_squares)
                        for destination in destination_bits:
                            yield Move(origin_square, destination, 0, 1)
        
        # Moving king
        piece_bit = bitboard[5]
        origin_square = find_least_significant_bit_set(piece_bit) # We get the indices of the squares pieces of this type are in
        non_capture_check_squares = precomputed_move_tables[5][origin_square] & ~(checks | all_own_pieces_bit| rays) # We get the precomputed moveable squares
        if non_capture_check_squares != 0: # If we can capture
            for destination in get_set_bit_indices(non_capture_check_squares):
                if self.king_is_safe(destination):
                    yield Move(origin_square, destination, 0, 0)

        


    def capture_moves(self):
        '''
        We create a set of moves and order them in terms of the score, returning a tuple of moves. This set of moves will always be computed before
        non_capture_moves so in this one we compute the next_unsafe_squares, also we are not yielding so we can compute all the next unsafe squares here before making the move.
        '''
        bitboard = self.bitboard
        all_own_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
        all_opp_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
        all_pieces_bit = all_own_pieces_bit | all_opp_pieces_bit
        self.get_pins_bits() # Computes the pins and stores the in self.pins and self.fake_pins (so that in non capture moves it is not necessary to compute)
        full_pins = 0
        for pin in self.pins:
            full_pins |= pin
        captures = []

        # Capturing with knight that are not pinned
        piece_bit = bitboard[1] & ~full_pins
        if piece_bit != 0: # If we have no pieces of the current type
            bit_indices = get_set_bit_indices(piece_bit) # We get the indices of the squares pieces of this type are in
            for origin_square in bit_indices: # For position of piece of this type
                moveable_squares = precomputed_move_tables[1][origin_square] # We get the precomputed moveable squares
                if moveable_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
                    for index in range(6,11): # For each of our opponent pieces, except king
                        capture_squares = moveable_squares & bitboard[index] # We get only squares in which opponent pieces are
                        if capture_squares != 0: # If we can capture
                            for destination in get_set_bit_indices(capture_squares):
                                captures.append(Move(origin_square, destination, 0, index)) # non-checks will have even is_check attribute 

        # Capturing with king
        piece_bit = bitboard[5]
        origin_square = find_least_significant_bit_set(piece_bit) # We get the indices of the squares pieces of this type are in
        moveable_squares = precomputed_move_tables[5][origin_square] # We get the precomputed moveable squares
        if moveable_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
            for index in range(6,11): # For each of our opponent pieces, except king
                capture_squares = moveable_squares & bitboard[index] # We get only squares in which opponent pieces are
                if capture_squares != 0: # If we can capture
                    for destination in get_set_bit_indices(capture_squares):
                        if self.king_is_safe(destination):
                            captures.append(Move(origin_square, destination, 0, index))

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
                            captures.append(Move(origin_square, destination, 0, index)) # checks will have odd is_check attribute

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
                            captures.append(Move(origin_square, destination, 0, index)) # checks will have odd is_check attribute
        
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
                            captures.append(Move(origin_square, destination, 0, index)) # checks will have odd is_check attribute
        
        # Capturing with pawns that are not pinned
        piece_bit = bitboard[0] & ~full_pins
        if piece_bit != 0: # If we can't move pawns
            pawn_indices = get_set_bit_indices(piece_bit) # The indices of the squares the pawns are in
            for origin_square in pawn_indices: # For position of piece of this type
                if self.turn: # White's turn
                    attacking_squares = precomputed_move_tables[6][origin_square] # We get the precomputed moveable squares
                    if attacking_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
                        for index in range(6,11): # For each of our opponent pieces, except king
                            capture_squares = attacking_squares & bitboard[index] # We get only squares in which opponent pieces are
                            if capture_squares != 0: # If we can capture
                                for destination in get_set_bit_indices(capture_squares):
                                    if destination in (56,57,58,59,60,61,62,63):
                                        captures.extend([Move(origin_square, destination, 4, index), Move(origin_square, destination, 3, index), 
                                                         Move(origin_square, destination, 2, index), Move(origin_square, destination, 1, index)])
                                    else:
                                        captures.append(Move(origin_square, destination, 0, index)) # checks will have odd is_check attribute
                else: # Blcak's turn
                    attacking_squares = precomputed_move_tables[7][origin_square] # We get the precomputed moveable squares
                    if attacking_squares & all_opp_pieces_bit != 0: # Current piece can't capture anything
                        for index in range(6,11): # For each of our opponent pieces, except king
                            capture_squares = attacking_squares & bitboard[index] # We get only squares in which opponent pieces are
                            if capture_squares != 0: # If we can capture
                                for destination in get_set_bit_indices(capture_squares):
                                    if destination in (0,1,2,3,4,5,6,7):
                                        captures.extend([Move(origin_square, destination, 4, index), Move(origin_square, destination, 3, index), 
                                                         Move(origin_square, destination, 2, index), Move(origin_square, destination, 1, index)])
                                    else:
                                        captures.append(Move(origin_square, destination, 0, index)) # checks will have odd is_check attribute

                if attacking_squares & passant_bitboards[self.psquare] != 0: # En passant capture
                    captures.append(Move(origin_square, find_least_significant_bit_set(passant_bitboards[self.psquare]), 0, 6))


        # Capturing with pinned pieces

        for pin in self.pins:
            # Capturing with rook that are pinned
            piece_bit = bitboard[3] & pin
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    if moveable_squares & all_opp_pieces_bit & pin != 0:
                        for index in range(6,11):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append(Move(origin_square, destination, 0, index)) # checks will have odd is_check attribute

            # Capturing with bishop that are pinned
            piece_bit = bitboard[2] & full_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    if moveable_squares & all_opp_pieces_bit & pin != 0:
                        for index in range(6,11):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append(Move(origin_square, destination, 0, index)) # checks will have odd is_check attribute
            
            # Capturing with queen that are pinned
            piece_bit = bitboard[4] & full_pins
            if piece_bit != 0:
                bit_indices = get_set_bit_indices(piece_bit)
                for origin_square in bit_indices:
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares |= long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    if moveable_squares & all_opp_pieces_bit & pin != 0:
                        for index in range(6,11):
                            capture_squares = moveable_squares & bitboard[index]
                            destination_bits = get_set_bit_indices(capture_squares)
                            for destination in destination_bits:
                                captures.append(Move(origin_square, destination, 0, index)) # checks will have odd is_check attribute
            
            # Capturing with pawns that are pinned
            piece_bit = bitboard[0] & full_pins
            if piece_bit != 0: # If we can't move pawns
                pawn_indices = get_set_bit_indices(piece_bit) # The indices of the squares the pawns are in
                for origin_square in pawn_indices: # For position of piece of this type
                    if self.turn:
                        attacking_squares = precomputed_move_tables[6][origin_square] # We get the precomputed moveable squares
                    else:
                        attacking_squares = precomputed_move_tables[7][origin_square] # We get the precomputed moveable squares
                    if attacking_squares & all_opp_pieces_bit & pin != 0: # Current piece can't capture anything
                        for index in range(6,11): # For each of our opponent pieces, except king
                            capture_squares = attacking_squares & bitboard[index] # We get only squares in which opponent pieces are
                            if capture_squares != 0: # If we can capture
                                for destination in get_set_bit_indices(capture_squares):
                                    captures.append(Move(origin_square, destination, 0, index)) # checks will have odd is_check attribute

        return [move for move in sorted(captures, key=lambda move: move.capture, reverse=True)] # return the moves ordered in terms of the score and make is_check = 0 for all

    def non_capture_moves(self):
        '''
        This will be a generator which when checking if move is a check it yields a move with score 1, else 0.
        '''
        bitboard = self.bitboard
        all_own_pieces_bit = bitboard[0] | bitboard[1] | bitboard[2] | bitboard[3] | bitboard[4] | bitboard[5]
        all_opp_pieces_bit = bitboard[6] | bitboard[7] | bitboard[8] | bitboard[9] | bitboard[10] | bitboard[11]
        all_pieces_bit = all_own_pieces_bit | all_opp_pieces_bit
        full_pins = 0
        for pin in self.pins:
            full_pins |= pin
        print('Pins:', self.pins)
        
        # Moving pieces that are not pinned

        # Knights
        piece_bit = bitboard[1] & ~full_pins
        if piece_bit != 0:
            for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                moveable_squares = precomputed_move_tables[1][origin_square] & ~all_pieces_bit # We get the precomputed moveable squares, note captures are computed on capture_moves().
                if moveable_squares != 0: # If we can move our piece
                    for destination in get_set_bit_indices(moveable_squares): # get_set_bit_indices is a generator so yielding bellow makes it more efficient
                        yield Move(origin_square, destination, 0, 0)

        # King 
        piece_bit = bitboard[5]
        origin_square = find_least_significant_bit_set(piece_bit) # For position of piece of this type
        moveable_squares = precomputed_move_tables[5][origin_square] & ~all_pieces_bit # We get the precomputed moveable squares, note captures are computed on capture_moves().
        if moveable_squares != 0: # If we can move our piece
            if self.turn and self.wc[0]: # If its whites turn with kingside castling rights
                if all_pieces_bit & 6 == 0: # If pieces are not blocking
                    if self.king_is_safe(4) and self.king_is_safe(2):
                        yield Move(0, 2, 0, -1) # Make the move as if rook moved (better for move method)

            if self.turn and self.wc[1]: # If its whites turn with queenside castling rights
                if all_pieces_bit & 112 == 0: # If pieces are not blocking
                    if self.king_is_safe(32) and self.king_is_safe(64):
                        yield Move(7, 4, 0, -1)

            if not self.turn and self.bc[0]: # If it's black turn with kingside castling rights
                if all_pieces_bit & 432345564227567616 == 0:
                    if self.king_is_safe(57) and self.king_is_safe(58):
                        yield Move(56, 58, 0, -1)
            
            if not self.turn and self.bc[1]: # If its black turn with queenside castling rights
                if all_pieces_bit & 8070450532247928832 == 0:
                    if self.king_is_safe(60) and self.king_is_safe(61):
                        yield Move(63, 60, 0, -1)
                
            for destination in get_set_bit_indices(moveable_squares): # get_set_bit_indices is a generator so yielding bellow makes it more efficient
                if self.king_is_safe(destination):
                    yield Move(origin_square, destination, 0, 0)
                            
        # Pawns
        piece_bit = bitboard[0] & ~full_pins
        if piece_bit != 0:
            for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                if self.turn:
                    moveable_squares = precomputed_move_tables[0][origin_square] & ~all_pieces_bit # We get rid of the squares in which our own or opp pieces are
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares): # Promotions
                            if destination in (63, 62, 61, 60, 59, 58, 57, 56):
                                yield Move(origin_square, destination, 4, 0)
                                yield Move(origin_square, destination, 3, 0)
                                yield Move(origin_square, destination, 2, 0)
                                yield Move(origin_square, destination, 1, 0)
                            else:
                                yield Move(origin_square, destination, 0, 0)
                else:
                    moveable_squares = precomputed_move_tables[8][origin_square] & ~all_pieces_bit # We get rid of the squares in which our own or opp pieces are
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares): # Promotions
                            if destination in (0, 1, 2, 3, 4, 5, 6, 7):
                                yield Move(origin_square, destination, 4, 0)
                                yield Move(origin_square, destination, 3, 0)
                                yield Move(origin_square, destination, 2, 0)
                                yield Move(origin_square, destination, 1, 0)
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

        for pin in self.pins:
            # Pinned Pawns
            piece_bit = bitboard[0] & pin
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    if self.turn:
                        moveable_squares = precomputed_move_tables[0][origin_square] & ~all_pieces_bit & pin # We get rid of the squares in which our own or opp pieces are
                    else:
                        moveable_squares = precomputed_move_tables[8][origin_square] & ~all_pieces_bit & pin # We get rid of the squares in which our own or opp pieces are
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)

            # Pinned Bishops
            piece_bit = bitboard[2] & pin
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares &= ~ all_pieces_bit
                    moveable_squares &= pin
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
            # Pinned Rooks
            piece_bit = bitboard[3] & pin
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    moveable_squares &= ~ all_pieces_bit
                    moveable_squares &= pin
                    if moveable_squares != 0:
                        for destination in get_set_bit_indices(moveable_squares):
                            yield Move(origin_square, destination, 0, 0)
            
            # Pinned Queens
            piece_bit = bitboard[4] & pin
            if piece_bit != 0:
                for origin_square in get_set_bit_indices(piece_bit): # For position of piece of this type
                    diag_moveable_squares = long_precomputed_bishop_table[origin_square][bishop_unfull_rays[origin_square] & (all_pieces_bit)]
                    diag_moveable_squares &= ~ all_pieces_bit
                    diag_moveable_squares &= pin
                    straight_moveable_squares = long_precomputed_rook_table[origin_square][rook_unfull_rays[origin_square] & (all_pieces_bit)]
                    straight_moveable_squares &= ~ all_pieces_bit
                    straight_moveable_squares &= pin
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
        bitboard = self.bitboard

        capture_indx = move.capture 

        # Switch roles
        new_bitboard = []

        # We go through opponent pieces
        if capture_indx == 6:
            if self.psquare != -1 and move.j in (256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 140737488355328, 70368744177664, 35184372088832, 17592186044416, 8796093022208, 4398046511104, 2199023255552, 1099511627776):
                if move.j % 8 + 8 == self.psquare and self.turn: # En passant capture
                    bitboard[6] &= ~(1 << (move.j - 8))
                    new_bitboard.append(bitboard[6])
                
                elif move.j % 8 == self.psquare and not self.turn: # En passant capture
                    bitboard[6] &= ~(1 << (move.j + 8))
                    new_bitboard.append(bitboard[6])

            else: # Pawn capture
                bitboard[6] &= ~(1 << move.j)
                new_bitboard.append(bitboard[6])
        
        else: # We haven't touched the opponent pawns
            new_bitboard.append(bitboard[6])

        for indx in range(7, 12): # Put opponents pieces at the start and take off if captured
            if indx == capture_indx: # If this is the piece we are capturing
                bitboard[indx] &= ~(1 << move.j)
            new_bitboard.append(bitboard[indx])

        # We go through our pieces
        if move.prom != 0: # If we are promoting pawn
            moving_piece = 0
            bitboard[0] &= ~(1 << move.i)
            bitboard[move.prom] |= 1 << move.j
            new_bitboard.append(bitboard[0])

        elif move.i in get_set_bit_indices(bitboard[0]): # If we are moving pawn
            moving_piece = 0
            bitboard[0] &= ~(1 << move.i)
            bitboard[0] |= 1 << move.j
            new_bitboard.append(bitboard[0])
        
        else:
            new_bitboard.append(bitboard[0])

        for indx in range(1,6): # Then put our pieces and change the moving one
            if move.i in get_set_bit_indices(bitboard[indx]): # If this is the piece we are moving
                moving_piece = indx
                bitboard[indx] &= ~(1 << move.i)
                bitboard[indx] |= 1 << move.j
            new_bitboard.append(bitboard[indx])
        
        # Castling (we must also move king)
        if capture_indx == -1 and move.i == 0: # White kingside castling
            new_bitboard[11] = 2
        elif capture_indx == -1 and move.i == 7: # White queenside castling
            new_bitboard[11] = 32
        elif capture_indx == -1 and move.i == 56: # Black kingside castling
            new_bitboard[11] = 144115188075855872
        elif capture_indx == -1 and move.i == 63: # Black queenside castling
            new_bitboard[11] = 2305843009213693952

        # Updating castling rights
        if moving_piece == 5 and self.turn: # If we move king castling rights are lost
            self.wc = [False, False]
        elif moving_piece == 5 and not self.turn: # If we move king castling rights are lost
            self.bc = [False, False]
        elif move.i == 0 or move.j == 0: # If we move rook on a1
            self.wc[0] = False
        elif move.i == 7 or move.j == 7: # If we move rook on h1
            self.wc[1] = False 
        elif move.i == 56 or move.j == 56: # If we move rook on a8
            self.bc[0] = False
        elif move.i == 63 or move.j == 63: # If we move rook on h8
            self.bc[1] = False

        # Update psquare if needed
        new_psquare = -1
        if self.turn and moving_piece == 0 and move.j - move.i == 16: # If we are moving a pawn twice
            new_psquare = move.i % 8 # We store the row to reduce size
        elif not self.turn and moving_piece == 0 and move.j - move.i == -16: # If we are moving a pawn twice
            new_psquare = (move.j % 8) + 8 # We store the row +8 to reduce the size
        print('New psquare:', new_psquare)
        return BitPosition(new_bitboard, new_psquare, self.wc, self.bc, not self.turn)

    def undo_move(self, move):
        '''
        Takes a move and undoes the move accordingly, updating all position attributes.
        '''

        return 0