import csv
from pathlib import Path

from Pydurma.aligners.aligner import TokenMatrix
from Pydurma.serializers.serializer import Serializer
from Pydurma.weighers.matrix_weigher import WeightMatrix
from Pydurma.utils.utils import get_top_weight_index


class CSVSerializer(Serializer):


    def __init__(self, weighted_token_matrix: TokenMatrix, output_dir: Path, text_id:str) -> None:
        super().__init__(weighted_token_matrix, output_dir, text_id)


    def get_token_entry(self, tokens, top_token_index):
        token_entry = []
        for token_index,token in enumerate(tokens):
            if token is None:
                token_string = ""
                token_weight = 0
            else:
                token_string = token[3]
                token_weight = token[4]
            if token_index == top_token_index:
                token_entry.append(f"[{token_string}_{token_weight}_]")
            else:
                token_entry.append(f"{token_string}_{token_weight}_")
        return token_entry

    def serialize_matrix(self):
            serialized_matrix = []
            for tokens_info in self.weighted_token_matrix:
                top_token_index = get_top_weight_index(tokens_info)
                token_entry = self.get_token_entry(tokens_info, top_token_index)
                serialized_matrix.append(token_entry)
            return serialized_matrix

    def save_serialized_matrix(self, serialized_matrix):
        output_file_path = self.output_dir / f"{self.text_id}.csv"
        with open(output_file_path, 'w', newline='') as csv_file:
            csv_writter = csv.writer(csv_file)
            csv_writter.writerows(serialized_matrix)
        return output_file_path




        

