from pathlib import Path

from CommonSpell.serializers.md import MdSerializer
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher
from CommonSpell.weighers.token_weigher_count import TokenCountWeigher


def test_md_serializer():
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
    expected_serialized_matrix = """བཀྲ་ཤིས་ཀུད་[^1]གྱི་[^2]བཀྲ་ཤིས་པའི[^3]།

[^1]: ཀུད་]V1: ཀུན་; V2,V3: ཀུད་;
[^2]: གྱི་]V1,V2: གྱི་; V3: ཀྱི་;
[^3]: པའི]V1,V2: པའི; V3: པས;
"""

    serializer = MdSerializer(token_matrix, tokenMatrixWeigher, weighers, output_dir=Path('tests/data/'))
    weighted_matrix = serializer.get_weighted_matix()
    serialized_matrix = serializer.serialize_matrix(weighted_matrix)

    assert serialized_matrix == expected_serialized_matrix

test_md_serializer()