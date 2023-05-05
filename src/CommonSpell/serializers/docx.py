from pathlib import Path
from pypandoc import convert_text
from typing import List

from CommonSpell.aligners.aligner import TokenMatrix
from CommonSpell.serializers.md import MdSerializer
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher, WeightMatrix
from CommonSpell.weighers.token_weigher import TokenWeigher

class DocxSerializer(MdSerializer):

    def __init__(self, token_matrix: TokenMatrix, tokenMatrixWeigher: TokenMatrixWeigher, weighers: List[TokenWeigher], output_dir: Path) -> None:
        super().__init__(token_matrix, tokenMatrixWeigher, weighers, output_dir)

    
    def serialize_matrix(self, weighted_matrix: WeightMatrix):
        return super().serialize_matrix(weighted_matrix)
    
    def save_serialized_matrix(self, serialized_matrix_md):
        output_path_file = self.output_dir / "common_spell.docx"
        convert_text(
        serialized_matrix_md, "docx", "markdown", outputfile=str(output_path_file)
        )
        return output_path_file