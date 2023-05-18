import tempfile
import pytest
from pathlib import Path


from CommonSpell.serializers.docx import DocxSerializer
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher
from CommonSpell.weighers.token_weigher_count import TokenCountWeigher


@pytest.mark.skip(reason="not able to install pandoc in github action for ci")
def test_docx_serializer():
    token_matrix = [
        [[0, 4, 1, 'བཀྲ་', 0], [0, 4, 1, 'བཀྲ་', 0], [0, 4, 1, 'བཀྲ་', 0]],
        [[4, 8, 1, 'ཤིས་', 0], [4, 8, 1, 'ཤིས་', 0], [4, 8, 1, 'ཤིས་', 0]],
        [[8, 12, 1, 'ཀུན་', 0], [8, 12, 1, 'ཀུད་', 0], [8, 12, 1, 'ཀུད་', 0]],
        [[12, 16, 1, 'གྱི་', 0], [12, 16, 1, 'གྱི་', 0], [12, 16, 1, 'ཀྱི་', 0]],
        [[16, 20, 1, 'བཀྲ་', 0], [16, 20, 1, 'བཀྲ་', 0], [16, 20, 1, 'བཀྲ་', 0]],
        [[20, 24, 1, 'ཤིས་', 0], [20, 24, 1, 'ཤིས་', 0], [20, 24, 1, 'ཤིས་', 0]],
        [[24, 25, 1, 'པའི', 0], [24, 25, 1, 'པའི', 0], [24, 25, 1, 'པས', 0]],
        [[25, 26, 1, '།', 0], [25, 26, 1, '།', 0], [25, 26, 1, '།', 0]]
    ]
    tokenMatrixWeigher = TokenMatrixWeigher()
    weighers = [TokenCountWeigher()]

    for weigher in weighers:
        tokenMatrixWeigher.add_weigher(weigher,weigher_weight=1)
    weighted_matrix = tokenMatrixWeigher.get_weight_matrix(token_matrix)
    

    with tempfile.TemporaryDirectory() as temp_dir:
        expected_serialized_matrix_path = Path(temp_dir) / 'common_spell.docx'

        serializer = DocxSerializer(token_matrix, token_matrix, output_dir=Path(temp_dir))
        serialized_matrix_md = serializer.serialize_matrix()
        serialized_matrix_path = serializer.save_serialized_matrix(serialized_matrix_md)


        assert serialized_matrix_path == expected_serialized_matrix_path

