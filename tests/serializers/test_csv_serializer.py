from pathlib import Path

from CommonSpell.serializers.csv import CSVSerializer
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher
from CommonSpell.weighers.token_weigher_count import TokenCountWeigher


def test_csv_serializer():
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
    expected_serialized_matrix = [
        ['[བཀྲ་_100_]','བཀྲ་_100_','བཀྲ་_100_'],
        ['[ཤིས་_100_]','ཤིས་_100_','ཤིས་_100_'],
        ['ཀུན་_33_','[ཀུད་_66_]','ཀུད་_66_'],
        ['[གྱི་_66_]','གྱི་_66_','ཀྱི་_33_'],
        ['[བཀྲ་_100_]','བཀྲ་_100_','བཀྲ་_100_'],
        ['[ཤིས་_100_]','ཤིས་_100_','ཤིས་_100_'],
        ['[པའི_66_]','པའི_66_','པས_33_'],
        ['[།_100_]','།_100_','།_100_'],
        ]
    for weigher in weighers:
        tokenMatrixWeigher.add_weigher(weigher, weigher_weight=1)
    weighted_matrix = tokenMatrixWeigher.get_weight_matrix(token_matrix)
    serializer = CSVSerializer(weighted_matrix, output_dir=Path('tests/data/'))
    serialized_matrix = serializer.serialize_matrix()

    assert serialized_matrix == expected_serialized_matrix