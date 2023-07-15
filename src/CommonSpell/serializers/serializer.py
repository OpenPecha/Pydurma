from pathlib import Path

from CommonSpell.aligners.aligner import TokenMatrix
from CommonSpell.weighers.matrix_weigher import WeightMatrix

class Serializer:

    def __init__(self, weighted_token_matrix: TokenMatrix, output_dir: Path, text_id:str) -> None:
        self.weighted_token_matrix = weighted_token_matrix
        self.output_dir = output_dir
        self.text_id = text_id

    def serialize_matrix(self):
        return None
    
    def save_serialized_matrix(self, serialized_matrix):
        return None