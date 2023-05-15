import csv
from pathlib import Path

from CommonSpell.aligners.aligner import TokenMatrix
from CommonSpell.serializers.serializer import Serializer
from CommonSpell.weighers.matrix_weigher import WeightMatrix
from CommonSpell.utils.utils import get_top_weight_index


class CSVSerializer(Serializer):


    def __init__(self, token_matrix: TokenMatrix, weighted_matrix:WeightMatrix, output_dir: Path) -> None:
        super().__init__(token_matrix, weighted_matrix, output_dir)


    def get_token_entry(self, tokens, weights, top_token_index):
        token_entry = []
        for token_index, (token, weight) in enumerate(zip(tokens, weights)):
            if token is None:
                token_string = ""
            else:
                token_string = token[3]
            if token_index == top_token_index:
                token_entry.append(f"[{token_string}_{weight}_]")
            else:
                token_entry.append(f"{token_string}_{weight}_")
        return token_entry

    def serialize_matrix(self):
            serialized_matrix = []
            for tokens, weights in zip(self.token_matrix, self.weighted_matrix):
                top_token_index = get_top_weight_index(weights)
                token_entry = self.get_token_entry(tokens, weights, top_token_index)
                serialized_matrix.append(token_entry)
            return serialized_matrix

    def save_serialized_matrix(self, serialized_matrix):
        output_file_path = self.output_dir / "common_spell.csv"
        with open(output_file_path, 'w', newline='') as csv_file:
            csv_writter = csv.writer(csv_file)
            csv_writter.writerows(serialized_matrix)
        return output_file_path




        

