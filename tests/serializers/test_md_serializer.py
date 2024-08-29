from pathlib import Path

from Pydurma.serializers.md import MdSerializer
from Pydurma.weighers.matrix_weigher import TokenMatrixWeigher
from Pydurma.weighers.token_weigher_count import TokenCountWeigher


def test_md_serializer():
    version_paths = [
        Path('./data/02-Narthang.txt'),
        Path('./data/01-Derge.txt'),
        Path('./data/03-Lhasa.txt'),
    ]
    versions_to_serialize = {
        '01-Derge': 'D',
        '02-Narthang': 'N'
        }
    
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
        tokenMatrixWeigher.add_weigher(weigher, weigher_weight=1)
    weighted_matrix = tokenMatrixWeigher.get_weight_matrix(token_matrix)

    expected_serialized_matrix = """བཀྲ་ཤིས་ཀུད་[^1]གྱི་[^2]བཀྲ་ཤིས་པའི[^3]།

[^1]: ཀུད་]D: ཀུན་; N: ཀུད་;
[^2]: གྱི་]D,N: གྱི་;
[^3]: པའི]D,N: པའི;
"""

    serializer = MdSerializer(weighted_matrix, 
                              output_dir=Path('tests/data/'), 
                              text_id='test',
                              version_paths=version_paths, 
                              verions_to_serialize=versions_to_serialize)
    serialized_matrix = serializer.serialize_matrix()

    assert serialized_matrix == expected_serialized_matrix
