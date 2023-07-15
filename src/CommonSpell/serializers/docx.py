from pathlib import Path
from typing import List
from pypandoc import convert_text

from CommonSpell.aligners.aligner import TokenMatrix
from CommonSpell.serializers.md import MdSerializer
from CommonSpell.weighers.matrix_weigher import WeightMatrix

class DocxSerializer(MdSerializer):

    def __init__(self, 
                 weighted_token_matrix: TokenMatrix, 
                 output_dir: Path, 
                 text_id:str,
                 version_paths: List[Path],
                 verions_to_serialize: List[str]) -> None:
        self.weighted_token_matrix = weighted_token_matrix
        self.output_dir = output_dir
        self.text_id = text_id
        self.version_paths = version_paths
        self.version_paths.sort()
        self.versions_to_serialize = verions_to_serialize

    
    def serialize_matrix(self):
        return super().serialize_matrix()
    
    def save_serialized_matrix(self, serialized_matrix_md):
        output_path_file = self.output_dir / f"{self.text_id}.docx"
        convert_text(
        serialized_matrix_md, "docx", "markdown", outputfile=str(output_path_file)
        )
        return output_path_file