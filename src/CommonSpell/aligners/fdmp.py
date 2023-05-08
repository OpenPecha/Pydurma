import logging

from fast_diff_match_patch import diff
from typing import Tuple, List, Dict

from CommonSpell.aligners.aligner import Aligner, TokenMatrix
from CommonSpell.aligners.post_processing_matrix import merge_consecutive_diff_tokens_entries
from CommonSpell.tokenizer import TokenList
from CommonSpell.utils.utils import *

# a diff returned by fdmp is a tuple with two values:
# - a character: '=', '-' or '+' with self-evident signification
# - an integer representing the number of characters
FDMPDiff = Tuple[str,int]

logger = logging.getLogger('FDMPaligner')

class FDMPaligner(Aligner):
    """
    Aligner using the fast_diff_match_patch (fdmp) library
    """

    @staticmethod
    def get_next_fdmp_diff_info(diffs: List[FDMPDiff], diff_i: int) -> Tuple[int, int, int, int]:
        """
        given the current index in the list of diffs, return a tuple with 4 integers:
        - the number of '-' in the next change
        - the number of '=' in the next change
        - the number of '+' in the next change
        - the new index in the list of diffs

        This is necessary because FDMP doesn't indicate "changed" tokens, only pure equality or gaps.
        So in a simple case like "ABC" vs. "ADC" it will output:
        [('=', 1), ('-', 1), ('+', 1), ('=', 1)]

        but this would result in an alignment matrix like

        AB-C
        A-DC

        which is not ideal, instead we combine an overlap of + and - into =, so that the
        resulting alignment matrix can look like

        ABC
        ADC

        When called in this example, this function will yield

        0, 1, 0, 1
        0, 1, 0, 3
        0, 1, 0, 4

        which simulates the output

        [('=', 1), ('=', 1), ('=', 1)]

        It could eventually be optimized to mimic the output of

        [('=', 3)]

        but the possible benefits are unclear.

        There is also the case where dmp will output a sequence of multiple + and - in a row
        so we need to have a while loop.
        """
        diff = diffs[diff_i]
        equal_c = 0
        minus_c = 0
        plus_c = 0
        if diff[0] == '=':
            equal_c = diff[1]
        elif diff[0] == '+':
            plus_c = diff[1]
        else:
            minus_c = diff[1]
        if plus_c > 0 or minus_c > 0:
            while diff_i + 1 < len(diffs) and diffs[diff_i+1][0] != "=":
                diff_i += 1
                diff = diffs[diff_i]
                if diff[0] == '+':
                    plus_c += diff[1]
                else:
                    minus_c += diff[1]
        diff_i += 1
        if plus_c > minus_c:
            equal_c += minus_c
            plus_c -= minus_c
            minus_c = 0
        elif minus_c > plus_c:
            equal_c += plus_c
            minus_c -= plus_c
            plus_c = 0
        elif minus_c > 0: 
            # in this case, minus_c == plus_c
            equal_c = plus_c
            plus_c = 0
            minus_c = 0
        return minus_c, equal_c, plus_c, diff_i

    @staticmethod
    def assert_diffs_correction(base_ts, other_ts, diffs):
        if not __debug__:
            return
        total_minus = 0
        total_equal = 0
        total_plus = 0
        for d in diffs:
            if d[0] == '=':
                total_equal += d[1]
            elif d[0] == '-':
                total_minus += d[1]
            else:
                total_plus += d[1]
        assert(total_equal + total_minus == len(base_ts))
        assert(total_equal + total_plus == len(other_ts))

    @staticmethod
    def assert_tokens_correction(ts, tokens):
        if not __debug__:
            return
        total_inc_t = 0
        for t in tokens:
            total_inc_t += t[2]
        assert(total_inc_t == len(ts))

    @staticmethod
    def assert_loop(diffs, diff_i, base_tokens, base_token_i, other_tokens, other_token_i):
        if not __debug__:
            return
        total_minus = 0
        total_equal = 0
        total_plus = 0
        for d in diffs[diff_i:]:
            if d[0] == '=':
                total_equal += d[1]
            elif d[0] == '-':
                total_minus += d[1]
            else:
                total_plus += d[1]
        remaining_base_ts_len = total_equal + total_minus
        remaining_other_ts_len = total_equal + total_plus
        total_inc_base_t = 0
        for t in base_tokens[base_token_i:]:
            total_inc_base_t += t[2]
        total_inc_other_t = 0
        for t in other_tokens[other_token_i:]:
            total_inc_other_t += t[2]
        logger.debug("remaining_other_ts_len = %d, remaining_other_tokens=%d, total_inc_other_t=%d", remaining_other_ts_len, len(other_tokens)-other_token_i-1, total_inc_other_t)
        assert(remaining_base_ts_len == total_inc_base_t)
        assert(remaining_other_ts_len == total_inc_other_t)

    @staticmethod
    def fill_cells_per_base_tokens(base_tokens: TokenList, other_tokens: TokenList, diffs: List[FDMPDiff], cells_per_base_tokens: List[int]) -> None:
        """
        This function is used to fill cells_per_base_tokens with some information from one witness:
        - base_tokens is the token list of the base witness
        - other_tokens is the token list of the other witness
        - diffs is the list of FDMP diffs between the base witness and the other witness

        In this context "base" indicates the first witness, which we will use to compare all the others.

        cells_per_base_tokens is a list of integers representing the number of cells necessary to
        contain all the aligned tokens for all the witnesses. The first integer represents
        the number of cells necessary to contain the tokens before the first base token.

        For instance (in a simplified notation), if we want to align "ABD" vs "ZABCYDE" into

        -AB-D-
        ZABCDE

        we need cells_per_base_tokens to be

        [1, 1, 2, 2]

        , representing:
        - 1 cell needed before the first base token 'A', to have room for 'Z'
        - 1 cell needed for the base token 'A', to align with 'A'
        - 2 cells needed for the base token 'B' to align with 'BC'
        - 2 cells needed for the base token 'D' to align with 'DE'

        This function only increments the values of cells_per_base_tokens if necessary
        so that it can be called for each witness.
        """
        base_token_i = 0
        other_token_i = 0
        len_other_tokens = len(other_tokens)
        len_base_tokens = len(base_tokens)
        last_equal_nb_other_tokens = 0
        logger.debug(diffs)
        logger.debug("fill_cells_per_base_tokens for nb_base_tokens=%d, nb_other_tokens=%d", len_base_tokens, len_other_tokens)
        diff_i = 0
        while diff_i < len(diffs):
            #FDMPaligner.assert_loop(diffs, diff_i, base_tokens, base_token_i, other_tokens, other_token_i)
            minus_c, equal_c, plus_c, next_diff_i = FDMPaligner.get_next_fdmp_diff_info(diffs, diff_i)
            logger.debug("new iteration with (%d -, %d =, %d +)", minus_c, equal_c, plus_c)
            if minus_c > 0:
                nb_base_ts_c = 0
                while base_token_i < len_base_tokens and nb_base_ts_c + base_tokens[base_token_i][2] <= minus_c:
                    nb_base_ts_c += base_tokens[base_token_i][2]
                    base_token_i += 1
                assert(nb_base_ts_c == minus_c)
            if equal_c > 0:
                nb_base_ts_c = 0
                nb_other_ts_c = 0
                while nb_base_ts_c < equal_c and base_token_i < len_base_tokens:
                    nb_base_tokens = 1
                    nb_other_tokens = 0
                    logger.debug("  new iteration: nb_base_ts_c = %d, nb_base_tokens = %d", nb_base_ts_c, nb_base_tokens)
                    # TODO: this won't work well for cases where one token has more than
                    # 1 characters in the string and the diff overlaps
                    nb_base_ts_c += base_tokens[base_token_i][2]
                    # add all tokens with 0 increment:
                    while base_token_i+nb_base_tokens < len_base_tokens and base_tokens[base_token_i+nb_base_tokens][2] < 1:
                        nb_base_tokens += 1
                    logger.debug("  nb_base_ts_c=%d, nb_base_tokens=%d, nb_other_ts_c=%d, other_tokens[other_token_i+nb_other_tokens][2]=%d, other_token_i+nb_other_tokens=%d/%d", nb_base_ts_c, nb_base_tokens, nb_other_ts_c, other_tokens[other_token_i][2], other_token_i+nb_other_tokens, len_other_tokens)
                    while other_token_i+nb_other_tokens < len_other_tokens and nb_other_ts_c + other_tokens[other_token_i+nb_other_tokens][2] <= nb_base_ts_c:
                        logger.debug("    new sub_iteration: nb_other_ts_c = %d, nb_other_tokens = %d, nb_other_ts_c += %d", nb_other_ts_c, nb_other_tokens, other_tokens[other_token_i+nb_other_tokens][2])
                        nb_other_ts_c += other_tokens[other_token_i+nb_other_tokens][2]
                        nb_other_tokens += 1
                    logger.debug("  add %d base and %d others", nb_base_tokens, nb_other_tokens)
                    # if there's more other tokens than there are base tokens, the
                    # final base token should have 1 + the difference
                    if nb_other_tokens > nb_base_tokens:
                        logger.debug("  set %d to max(%d)", base_token_i+nb_base_tokens, 1 + nb_other_tokens - nb_base_tokens)
                        cells_per_base_tokens[base_token_i+nb_base_tokens] = max(cells_per_base_tokens[base_token_i+nb_base_tokens], 1 + nb_other_tokens - nb_base_tokens)
                    base_token_i += nb_base_tokens
                    other_token_i += nb_other_tokens
                    last_equal_nb_other_tokens = nb_other_tokens
                assert(nb_base_ts_c == equal_c)
                assert(nb_other_ts_c == equal_c)
            if plus_c > 0:
                nb_other_ts_c = 0
                nb_other_tokens = 0
                while other_token_i+nb_other_tokens < len_other_tokens and nb_other_ts_c + other_tokens[other_token_i+nb_other_tokens][2] <= plus_c:
                    nb_other_ts_c += other_tokens[other_token_i+nb_other_tokens][2]
                    nb_other_tokens += 1
                if diff_i > 0:
                    cells_per_base_tokens[base_token_i] = max(cells_per_base_tokens[base_token_i], nb_other_tokens + last_equal_nb_other_tokens)
                else:
                    # special case for the first cell of the list, which is 0 by default, not 1
                    cells_per_base_tokens[base_token_i] = max(cells_per_base_tokens[base_token_i], nb_other_tokens)
                logging.debug("nb_other_ts_c = %d, nb_other_tokens = %d", nb_other_ts_c, nb_other_tokens)
                other_token_i += nb_other_tokens
                assert(nb_other_ts_c == plus_c)
            if equal_c == 0:
                last_equal_nb_other_tokens = 0
            diff_i = next_diff_i
        assert(other_token_i == len(other_tokens))
        assert(base_token_i == len(base_tokens))
        logger.debug("fill_cells_per_base_tokens done with base_token_i = %d, other_token_i = %d", base_token_i, other_token_i)
        logger.debug(cells_per_base_tokens)


    @staticmethod
    def fill_base_column(matrix: TokenMatrix, base_tokens: TokenList, cells_per_base_tokens: List[int]) -> TokenList:
        """
        Returns the first row of the matrix.
        - base_tokens is the list of tokens of the base witness
        - cells_per_base_tokens: see fill_cells_per_base_tokens
        - total_sum is the length of the rows in the matrix (all have the same)
        """
        matrix_row_i = cells_per_base_tokens[0]
        for i, t in enumerate(base_tokens):
            matrix[matrix_row_i][0] = t
            matrix_row_i += cells_per_base_tokens[i+1]

    @staticmethod
    def fill_other_column(matrix: TokenMatrix, column_i: int, base_tokens: TokenList, other_tokens: TokenList, diffs: List[FDMPDiff], cells_per_base_tokens: List[int]) -> TokenList:
        """
        Returns the row of a matrix for a witness
        - base_tokens is the list of tokens of the base witness
        - other_tokens is the list of tokens of a witness
        - diffs is the list of FDMP diffs between the base and the witness
        - cells_per_base_tokens: see fill_cells_per_base_tokens
        - total_sum is the length of the rows in the matrix (all have the same)
        """
        len_matrix = len(matrix)
        matrix_row_i = cells_per_base_tokens[0]
        base_token_i = 0
        other_token_i = 0
        len_base_tokens = len(base_tokens)
        len_other_tokens = len(other_tokens)
        last_equal_nb_other_tokens = 0
        diff_i = 0
        logger.debug("len_base_tokens=%d", len_base_tokens)
        logger.debug(base_tokens)
        logger.debug(other_tokens)
        logger.debug(diffs)
        logger.debug(cells_per_base_tokens)
        while diff_i < len(diffs):
            debug_token_matrix(logger, matrix)
            FDMPaligner.assert_loop(diffs, diff_i, base_tokens, base_token_i, other_tokens, other_token_i)
            minus_c, equal_c, plus_c, next_diff_i = FDMPaligner.get_next_fdmp_diff_info(diffs, diff_i)
            logger.debug("iteration with (%d -, %d =, %d +), matrix_row_i = %d/%d, other_token_i = %d/%d", minus_c, equal_c, plus_c, matrix_row_i, len_matrix, other_token_i, len_other_tokens)
            # at any point in time, the number of columns left in the matrix should be (by design)
            # higher or equal to the number of tokens left:
            #assert(len_matrix - matrix_row_i >= len_other_tokens - other_token_i)
            if minus_c > 0:
                nb_base_ts_c = 0
                while base_token_i < len_base_tokens and nb_base_ts_c + base_tokens[base_token_i][2] <= minus_c:
                    logger.debug("  other_row '-', matrix_row_i=%d/%d, base_token_i=%d, iteration because %d < %d", matrix_row_i, len_matrix, base_token_i, nb_base_ts_c, minus_c)
                    nb_base_ts_c += base_tokens[base_token_i][2]
                    matrix_row_i += cells_per_base_tokens[base_token_i+1]
                    base_token_i += 1
            if equal_c > 0:
                nb_base_ts_c = 0
                nb_other_ts_c = 0
                while nb_base_ts_c < equal_c and base_token_i < len_base_tokens:
                    last_equal_nb_other_tokens = 0
                    #assert(len_matrix - matrix_row_i >= len_other_tokens - other_token_i)
                    logger.debug("  other_row '=', matrix_row_i=%d/%d, base_token_i=%d, iteration because %d < %d", matrix_row_i, len_matrix, base_token_i, nb_base_ts_c, equal_c)
                    debug_token_matrix(logger, matrix)
                    # iterate on all tokens with 0 increment:
                    total_nb_base_ts_c_increment = 0
                    matrix_row_next_i = matrix_row_i
                    while base_token_i < len_base_tokens and total_nb_base_ts_c_increment + base_tokens[base_token_i][2] < 2:
                        total_nb_base_ts_c_increment += base_tokens[base_token_i][2]
                        base_token_i += 1
                        matrix_row_next_i += cells_per_base_tokens[base_token_i]
                    #logger.debug("  total_nb_base_ts_c_increment=%d" % total_nb_base_ts_c_increment)
                    nb_base_ts_c += total_nb_base_ts_c_increment
                    logger.debug("  matrix_row_next_i=%d, nb_other_ts_c=%d, nb_base_ts_c=%d", matrix_row_next_i, nb_other_ts_c, nb_base_ts_c)
                    while other_token_i < len_other_tokens and nb_other_ts_c + other_tokens[other_token_i][2] <= nb_base_ts_c:
                        logger.debug("    sub-iteration because %d <= %d", nb_other_ts_c, nb_base_ts_c)
                        debug_token_matrix(logger, matrix)
                        other_token = other_tokens[other_token_i]
                        nb_other_ts_c += other_token[2]
                        logger.debug("    set matrix_row_i=%d/%d, column_i=%d, nb_other_ts_c=%d", matrix_row_i, len_matrix, column_i, nb_other_ts_c)
                        matrix[matrix_row_i][column_i] = other_token
                        matrix_row_i += 1
                        other_token_i += 1
                        last_equal_nb_other_tokens += 1
                    logger.debug("  set matrix_row_i to matrix_row_next_i=%d", matrix_row_next_i)
                    matrix_row_i = matrix_row_next_i
            if plus_c > 0:
                if diff_i > 0:
                    # general case
                    matrix_row_next_i = matrix_row_i
                    logger.debug("base_token_i=%d" % base_token_i)
                    matrix_row_i -= cells_per_base_tokens[base_token_i]-last_equal_nb_other_tokens
                    logger.debug("  other_row '+', matrix_row_i = %d (%d) => %d/%d, other_token_i = %d", matrix_row_next_i, last_equal_nb_other_tokens, matrix_row_i, len_matrix, other_token_i)
                    nb_other_ts_c = 0
                    while other_token_i < len_other_tokens and nb_other_ts_c + other_tokens[other_token_i][2] <= plus_c:
                        other_token = other_tokens[other_token_i]
                        nb_other_ts_c += other_token[2]
                        logger.debug("  set %d to other_token %s (len=%d)", matrix_row_i, other_token, len_matrix)
                        matrix[matrix_row_i][column_i] = other_token
                        #logger.debug(matrix)
                        matrix_row_i += 1
                        other_token_i += 1
                    matrix_row_i = matrix_row_next_i
                else:
                    # special case for insertions before the first base token, we insert from right to left
                    # TODO: tokens of size 0 should be on the right
                    matrix_row_next_i = matrix_row_i
                    matrix_row_i -= 1
                    nb_other_ts_c = 0
                    tokenlist = []
                    while other_token_i < len_other_tokens and nb_other_ts_c + other_tokens[other_token_i][2] <= plus_c:
                        nb_other_ts_c += other_tokens[other_token_i][2]
                        tokenlist.append(other_tokens[other_token_i])
                        other_token_i += 1
                    tokenlist.reverse()
                    for t in tokenlist:
                        matrix[matrix_row_i][column_i] = t
                        matrix_row_i -= 1
                    matrix_row_i = matrix_row_next_i
            if equal_c == 0:
                last_equal_nb_other_tokens = 0
            diff_i = next_diff_i
        assert(matrix_row_i == len_matrix)


    def get_alignment_matrix(self, token_strings: List[str], token_lists: List[TokenList]) -> TokenMatrix:
        """
        A function that takes as arguments:
        - a list of token_strings (one row per witness)
        - a list of token lists (one row per witness)

        token_strings and token lists are typically the result of the tokenize() function of a Tokenizer

        It returns an alignment matrix in the form of a matrix of tokens, one row per witness.
        Gaps in the matrix have the value None.
        """
        matrix = []
        base_tokens = token_lists.pop(0)
        base_token_string = token_strings.pop(0)
        FDMPaligner.assert_tokens_correction(base_token_string, base_tokens)
        cells_per_base_tokens = [1] * (len(base_tokens)+1)
        cells_per_base_tokens[0] = 0
        # compute the diffs with fdmp
        diff_lists = []
        for token_index, other_token_string in enumerate(token_strings):
            diffs = diff(base_token_string, other_token_string, checklines=0, cleanup=None)
            #FDMPaligner.assert_diffs_correction(base_token_string, other_token_string, diffs)
            diff_lists.append(diffs)
            other_tokens = token_lists[token_index]
            #FDMPaligner.assert_tokens_correction(other_token_string, other_tokens)
            # update cells_per_base_tokens
            FDMPaligner.fill_cells_per_base_tokens(base_tokens, other_tokens, diffs, cells_per_base_tokens)
        
        # initialize the matrix:
        matrix = [[None for _ in range(len(token_lists)+1) ] for _ in range(sum(cells_per_base_tokens))]
        # special case for the first row corresponding to the base witness
        FDMPaligner.fill_base_column(matrix, base_tokens, cells_per_base_tokens)
        for version_index, diffs in enumerate(diff_lists):
            FDMPaligner.fill_other_column(matrix, version_index+1, base_tokens, token_lists[version_index], diffs, cells_per_base_tokens)
        matrix = merge_consecutive_diff_tokens_entries(matrix)
        return matrix