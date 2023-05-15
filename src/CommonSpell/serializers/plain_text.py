from pathlib import Path

from CommonSpell.aligners.aligner import TokenMatrix
from CommonSpell.serializers.serializer import Serializer
from CommonSpell.weighers.matrix_weigher import WeightMatrix
from CommonSpell.utils.utils import get_top_weight_index

class PlainTextSerializer(Serializer):


    def __init__(self, token_matrix: TokenMatrix, weighted_matrix: WeightMatrix, output_dir: Path) -> None:
        super().__init__(token_matrix, weighted_matrix, output_dir)

    
    def serialize_matrix(self):
        serialized_matrix = ''
        for tokens, weights in zip(self.token_matrix, self.weighted_matrix):
            top_token_index = get_top_weight_index(weights)
            try:
                voted_token = tokens[top_token_index][3]
            except:
                voted_token = ''
            serialized_matrix += voted_token
        return serialized_matrix
    
    def save_serialized_matrix(self, serialized_matrix):
        output_file_path = self.output_dir / "common_spell.txt"
        output_file_path.write_text(serialized_matrix, encoding='utf-8')
        return output_file_path

        