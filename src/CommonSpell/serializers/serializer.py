from pathlib import Path

from CommonSpell.aligners.aligner import TokenMatrix
from CommonSpell.weighers.matrix_weigher import WeightMatrix

class Serializer:

    def __init__(self, token_matrix: TokenMatrix, weighted_matrix: WeightMatrix, output_dir: Path) -> None:
        self.token_matrix = token_matrix
        self.weighted_matrix = weighted_matrix
        self.output_dir = output_dir

    def serialize_matrix(self):
        return None
    
    def save_serialized_matrix(self, serialized_matrix):
        return None