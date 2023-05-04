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
            self.token_matrix_weigher.add_weigher(weigher)
        weighed_matrix = self.token_matrix_weigher.get_weight_matrix(self.token_matrix)
        return weighed_matrix
    
    
    def serialize_matrix(self, weighted_matrix: WeightMatrix):
        return None