from typing import List

from CommonSpell.aligners.aligner import TokenMatrix
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher, WeightMatrix
from CommonSpell.weighers.token_weigher import TokenWeigher

class Serializer:

    def __init__(self, token_matrix: TokenMatrix, tokenMatrixWeigher: TokenMatrixWeigher, weighers: List[TokenWeigher], output_dir) -> None:
        self.token_matrix = token_matrix
        self.token_matrix_weigher = tokenMatrixWeigher
        self.weighers = weighers
        self.output_dir = output_dir

    
    def get_weighted_matix(self):
        for weigher in self.weighers:
            self.token_matrix_weigher.add_weigher(weigher, 1)
        weighed_matrix = self.token_matrix_weigher.get_weight_matrix(self.token_matrix)
        return weighed_matrix
    
    def get_top_weight_index(self, weights):
        top_weight = 0
        top_token_index = 0
        for j, weight in enumerate(weights):
            if weight is not None and weight > top_weight:
                top_weight = weight
                top_token_index = j
        return top_token_index

    def get_token_strings(self, tokens):
        token_strings = {}
        for version_index, token in enumerate(tokens,1):
            token_strings[f'V{version_index}'] = token[3]
        return token_strings
    
    def is_diff_token(self, tokens):
        token_strings = self.get_token_strings(tokens)
        if len(list(set(token_strings.values()))) == 1:
            return False
        return True
    
    
    def serialize_matrix(self, weighted_matrix: WeightMatrix):
        return None
    
    def save_serialized_matrix(self, serialized_matrix):
        return None