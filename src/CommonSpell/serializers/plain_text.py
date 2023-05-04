import csv
from typing import List
from CommonSpell.aligners.aligner import TokenMatrix

from CommonSpell.serializers.serializer import Serializer
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher, WeightMatrix
from CommonSpell.weighers.token_weigher import TokenWeigher

class PlainTextSerializer(Serializer):


    def __init__(self, token_matrix: TokenMatrix, tokenMatrixWeigher: TokenMatrixWeigher, weighers: List[TokenWeigher], output_dir) -> None:
        super().__init__(token_matrix, tokenMatrixWeigher, weighers, output_dir)

    
    def serialize_matrix(self, weighted_matrix: WeightMatrix):
        serialized_matrix = ''
        for row_i, tokens in enumerate(self.token_matrix):
            top_token_index = 0
            weights = weighted_matrix[row_i]
            top_token_index = self.get_top_weight_index(weights)
            voted_token = tokens[top_token_index][3]
            serialized_matrix += voted_token
        return serialized_matrix
    
    def save_serialized_matrix(self, serialized_matrix):
        output_file_path = self.output_dir / "common_spell.txt"
        output_file_path.write_text(serialized_matrix, encoding='utf-8')
        return output_file_path

        