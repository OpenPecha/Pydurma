from pathlib import Path

from CommonSpell.aligners.aligner import TokenMatrix
from CommonSpell.serializers.serializer import Serializer
from CommonSpell.weighers.matrix_weigher import WeightMatrix
from CommonSpell.utils.utils import get_top_weight_index

class PlainTextSerializer(Serializer):


    def __init__(self, weighted_token_matrix: TokenMatrix, output_dir: Path, text_id:str) -> None:
        super().__init__(weighted_token_matrix, output_dir, text_id)

    
    def serialize_matrix(self):
        serialized_matrix = ''
        for tokens_info in self.weighted_token_matrix:
            top_token_index = get_top_weight_index(tokens_info)
            try:
                voted_token = tokens_info[top_token_index][3]
            except:
                voted_token = ''
            serialized_matrix += voted_token
        return serialized_matrix
    
    def save_serialized_matrix(self, serialized_matrix):
        output_file_path = self.output_dir / f"{self.text_id}.txt"
        output_file_path.write_text(serialized_matrix, encoding='utf-8')
        return output_file_path

        