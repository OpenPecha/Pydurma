from typing import List, Tuple

from vulgatizer.weighers.token_weigher import TokenWeigher
from vulgatizer.vulgaligners.vulgaligner import TokenMatrix
from vulgatizer.tokenizer import Token, TokenList

WeightedWeights = Tuple[List[int], int]
WeightedWeighers = Tuple[TokenWeigher, int]
WeightMatrix = List[List[int]]

class TokenMatrixWeigher():
    """
    This class produces a weight matrix with the same dimensions and structure as the token matrix.

    It is initialized by adding TokenWeighers and assigning a weight to each of them.
    """

    def __init__(self, weigh_identical_rows = False):
        self.weighted_weighters: List[WeightedWeighers] = []
        # whether or not to weigh in the case where all tokens are identical in a column
        self.weigh_identical_rows = weigh_identical_rows

    def add_weigher(self, weigher: TokenWeigher, weigher_weight: int):
        """
        Add a weigher
        """
        self.weighted_weighters.append((weigher, weigher_weight))

    def is_the_same_token(self, tokens):
        first_token_string = None
        for token in tokens:
            if token is None:
                # if there's a gap, then not all the tokens are the same, by design
                return False
            if first_token_string is None:
                first_token_string = token[3]
            elif token[3] != first_token_string:
                return False
        return True

    def get_row_weighted_weights(self, tokens: List[Token]) -> List[WeightedWeights]:
        """
        Get the weighted weights by running a column through the weighers
        """
        result = []
        if self.weigh_identical_rows and self.is_the_same_token(tokens):
            return None
        for (weigher, weigher_weight) in self.weighted_weighters:
            result.append((weigher.weigh(tokens), weigher_weight, weigher.relative))
        return result

    def fill_average_row_weights(self, token_matrix, weight_matrix, row_index: int):
        """
        Get the weighted average of the weights for a column
        """
        row_weighted_weights = self.get_row_weighted_weights(token_matrix[row_index])
        # optimization: if all the tokens are identical, we don't weigh them
        if row_weighted_weights is None:
            return
        # optimization: with only one weigher, we just use its output
        if len(row_weighted_weights) == 1:
            weights = row_weighted_weights[0][0]
            for col_index, weight in enumerate(weights):
                weight_matrix[row_index][col_index] = weight
            return
        nb_columns = len(token_matrix[0])
        # prepare the weighted average calculation
        absolute_weight_sums: List[int] = [0 for _ in range(nb_columns)]
        relative_weight_sums: List[int] = [0 for _ in range(nb_columns)]
        absolute_weight_totals: List[int] = [0 for _ in range(nb_columns)]
        relative_weight_totals: List[int] = [0 for _ in range(nb_columns)]
        for (weights, weights_weight, weigher_relative) in row_weighted_weights:
            for col_index, weight in enumerate(weights):
                if weight is None:
                    continue
                if weigher_relative:
                    relative_weight_sums[col_index] += weight * weights_weight
                    relative_weight_totals[col_index] += weights_weight
                else:
                    absolute_weight_sums[col_index] += weight * weights_weight
                    absolute_weight_totals[col_index] += weights_weight
        for col_index, weight_total in enumerate(absolute_weight_totals):
            if weight_total > 0:
                weight = absolute_weight_sums[col_index] // weight_total
                if relative_weight_sums[col_index] > 0:
                    relative_weight = relative_weight_sums[col_index] // relative_weight_totals[col_index]
                    weight = int(weight * relative_weight / 100)
                weight_matrix[row_index][col_index] = weight

    def get_weight_matrix(self, token_matrix: TokenMatrix) -> WeightMatrix:
        """
        Returns a matrix with the same dimensions as the TokenMatrix, containing the
        final weight of each token, averaged between the different weighers.

        TODO: TokenMatrix and this matrix should probably instead by numpy arrays.
        """
        nb_rows = len(token_matrix)
        nb_columns = len(token_matrix[0])
        if len(self.weighted_weighters) == 0:
            return None
        weight_matrix: WeightMatrix = [[None for _ in range(nb_columns)] for _ in range(nb_rows)]
        for row_index in range(nb_rows):
            self.fill_average_row_weights(token_matrix, weight_matrix, row_index)
        return weight_matrix


if __name__ == "__main__":
    from token_weigher_count import TokenCountWeigher
    from token_weigher_valid_bo import ValidBoTokenWeigher
    # token_matrix = [[(0, 5, 1, '༄༅། །'), (0, 5, 1, '༄༅། །'), (0, 5, 1, '༄༅། །'), (0, 4, 1, '༄། །'), (0, 5, 1, '༄༅། །'), None]]
    token_matrix = [
        [(436, 437, 1, '།'), (454, 462, 1, 'སྒྲོགས་ '), (433, 435, 1, '༐།'), None, None, None],
        [(568, 575, 1, 'ཀྱེལ་་\n'), None, (566, 569, 1, 'ལ་\n'), (585, 589, 1, 'ལ་་\n'), None, (585, 589, 1, 'ལ་་\n')],
        [(519, 526, 1, 'ཇི་\n་་་'), (542, 546, 1, 'ཇི་\n'), (511, 515, 1, 'ཇི་\n'), (527, 531, 1, 'ཤོག\n'), (526, 530, 1, 'ཤོག\n'), (527, 531, 1, 'ཤོག\n')],
        [(848, 852, 1, 'བ་་\n'), (861, 866, 1, 'བ་་་\n'), (830, 834, 1, 'བ་་\n'), None, None, None],
        [(618, 621, 1, 'གི་'), (635, 638, 1, 'གི་'), (604, 607, 1, 'གི་'), (620, 623, 1, 'གི་'), (617, 620, 1, 'གི་'), (620, 623, 1, 'གི་')],
        [(123, 124, 1, 'བ'), None, (120, 122, 1, '('), None, None, None]
        ]
    row_index = 5
    weight_matrix = [[None for _ in range(len(token_matrix[0]))] for _ in range(len(token_matrix))]
    weigher = TokenMatrixWeigher()
    # assert(weigher.is_the_same_token([(0,0,0,"a"), (0,0,0,"a"), (0,0,0,"a")]))
    # assert(not weigher.is_the_same_token([(0,0,0,"a"), (0,0,0,"q"), (0,0,0,"a")]))
    # assert(not weigher.is_the_same_token([(0,0,0,"a"), None, (0,0,0,"a")]))
    weigher.add_weigher(TokenCountWeigher(), 1)
    weigher.add_weigher(ValidBoTokenWeigher(), 1)
    # weigher.add_weigher(ValidBoTokenWeigher(), 1)
    weigher.fill_average_row_weights(token_matrix, weight_matrix, row_index)
    print(weight_matrix)
    expected_weight_matrix = [[68, 68, 68, 43, 68, 16]]
    assert expected_weight_matrix == weight_matrix