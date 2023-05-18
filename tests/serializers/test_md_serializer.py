from pathlib import Path

from CommonSpell.serializers.md import MdSerializer
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher
from CommonSpell.weighers.token_weigher_count import TokenCountWeigher


def test_md_serializer():
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
        tokenMatrixWeigher.add_weigher(weigher, weigher_weight=1)
    weighted_matrix = tokenMatrixWeigher.get_weight_matrix(token_matrix)

    expected_serialized_matrix = """བཀྲ་ཤིས་ཀུད་[^1]གྱི་[^2]བཀྲ་ཤིས་པའི[^3]།

[^1]: ཀུད་]V1: ཀུན་; V2,V3: ཀུད་;
[^2]: གྱི་]V1,V2: གྱི་; V3: ཀྱི་;
[^3]: པའི]V1,V2: པའི; V3: པས;
"""

    serializer = MdSerializer(weighted_matrix, output_dir=Path('tests/data/'))
    serialized_matrix = serializer.serialize_matrix()

    assert serialized_matrix == expected_serialized_matrix
