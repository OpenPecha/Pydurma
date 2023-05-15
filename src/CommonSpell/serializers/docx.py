from pathlib import Path
from pypandoc import convert_text

from CommonSpell.aligners.aligner import TokenMatrix
from CommonSpell.serializers.md import MdSerializer
from CommonSpell.weighers.matrix_weigher import WeightMatrix

class DocxSerializer(MdSerializer):

    def __init__(self, token_matrix: TokenMatrix, weighted_matrix: WeightMatrix, output_dir: Path) -> None:
        super().__init__(token_matrix, weighted_matrix, output_dir)

    
    def serialize_matrix(self):
        return super().serialize_matrix()
    
    def save_serialized_matrix(self, serialized_matrix_md):
        output_path_file = self.output_dir / "common_spell.docx"
        convert_text(
        serialized_matrix_md, "docx", "markdown", outputfile=str(output_path_file)
        )
        return output_path_file