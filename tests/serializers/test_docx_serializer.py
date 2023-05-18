import tempfile
import pytest
from pathlib import Path


from CommonSpell.serializers.docx import DocxSerializer
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher
from CommonSpell.weighers.token_weigher_count import TokenCountWeigher


@pytest.mark.skip(reason="not able to install pandoc in github action for ci")
def test_docx_serializer():
    token_matrix = [
        [(0, 4, 1, 'བཀྲ་'), (0, 4, 1, 'བཀྲ་'), (0, 4, 1, 'བཀྲ་')],
        [(4, 8, 1, 'ཤིས་'), (4, 8, 1, 'ཤིས་'), (4, 8, 1, 'ཤིས་')],
        [(8, 12, 1, 'ཀུན་'), (8, 12, 1, 'ཀུད་'), (8, 12, 1, 'ཀུད་')],
        [(12, 16, 1, 'གྱི་'), (12, 16, 1, 'གྱི་'), (12, 16, 1, 'ཀྱི་')],
        [(16, 20, 1, 'བཀྲ་'), (16, 20, 1, 'བཀྲ་'), (16, 20, 1, 'བཀྲ་')],
        [(20, 24, 1, 'ཤིས་'), (20, 24, 1, 'ཤིས་'), (20, 24, 1, 'ཤིས་')],
        [(24, 25, 1, 'པའི'), (24, 25, 1, 'པའི'), (24, 25, 1, 'པས')],
        [(25, 26, 1, '།'), (25, 26, 1, '།'), (25, 26, 1, '།')]
    ]
    tokenMatrixWeigher = TokenMatrixWeigher()
    weighers = [TokenCountWeigher()]

    for weigher in weighers:
        tokenMatrixWeigher.add_weigher(weigher,weigher_weight=1)
    weighted_matrix = tokenMatrixWeigher.get_weight_matrix(token_matrix)
    

    with tempfile.TemporaryDirectory() as temp_dir:
        expected_serialized_matrix_path = Path(temp_dir) / 'common_spell.docx'

        serializer = DocxSerializer(weighted_matrix, output_dir=Path(temp_dir))
        serialized_matrix_md = serializer.serialize_matrix()
        serialized_matrix_path = serializer.save_serialized_matrix(serialized_matrix_md)


        assert serialized_matrix_path == expected_serialized_matrix_path

