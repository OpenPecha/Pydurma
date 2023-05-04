import csv
from typing import List
from CommonSpell.aligners.aligner import TokenMatrix

from CommonSpell.serializers.serializer import Serializer
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher, WeightMatrix
from CommonSpell.weighers.token_weigher import TokenWeigher


class CSVSerializer(Serializer):


    def __init__(self, token_matrix: TokenMatrix, tokenMatrixWeigher: TokenMatrixWeigher, weighers: List[TokenWeigher], output_dir) -> None:
        super().__init__(token_matrix, tokenMatrixWeigher, weighers, output_dir)


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

    def serialize_matrix(self, weighted_matrix: WeightMatrix):
        output_file_path = self.output_dir / "common_spell.csv"
        with open(output_file_path, 'w', newline='') as csv_file:
            csv_writter = csv.writer(csv_file)
            for row_i, tokens in enumerate(self.token_matrix):
                top_weight = 0
                top_token_index = 0
                weights = weighted_matrix[row_i]
                for j, weight in enumerate(weights):
                    if weight is not None and weight > top_weight:
                        top_weight = weight
                        top_token_index = j
                token_entry = self.get_token_entry(tokens, weight, top_token_index)
                csv_writter.writerow(token_entry)




        

