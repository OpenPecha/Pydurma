from pathlib import Path
from typing import List

from CommonSpell.aligners.aligner import TokenMatrix
from CommonSpell.serializers.serializer import Serializer
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher, WeightMatrix
from CommonSpell.weighers.token_weigher import TokenWeigher
from CommonSpell.utils.utils import is_diff_token, get_token_strings



class MdSerializer(Serializer):

    def __init__(self, token_matrix: TokenMatrix, tokenMatrixWeigher: TokenMatrixWeigher, weighers: List[TokenWeigher], output_dir: Path) -> None:
        super().__init__(token_matrix, tokenMatrixWeigher, weighers, output_dir)

    def regroup_same_diffs(self, diff_tokens):
        regrouped_notes = {}
        for version_name, diff_string in diff_tokens.items():
            regrouped_notes[diff_string] = [version_name] if diff_string not in regrouped_notes.keys() else regrouped_notes[diff_string] + [version_name]
        for diff_string, versions in regrouped_notes.items():
            versions.sort()
            regrouped_notes[diff_string] = versions
        return regrouped_notes

    def get_footnote_text(self, diff_tokens, voted_token):
        note_text = f'{voted_token}] '
        diff_token_strings = get_token_strings(diff_tokens)
        regrouped_notes = self.regroup_same_diffs(diff_token_strings)
        for diff_string, verions in regrouped_notes.items():
            if diff_string == voted_token:
                continue
            version_names = ','.join(verions)
            note_text += f"{version_names}: {diff_string}; "
        return note_text[:-1]
        
    def serialize_matrix(self, weighted_matrix: WeightMatrix):
        diff_note_walker = 1
        token_walker = 0
        serialized_body_text_md = ''
        serialized_footnote_text_md = ''
        serialized_matrix_md = ''
        for tokens, weights in zip(self.token_matrix, weighted_matrix):
            top_token_index = self.get_top_weight_index(weights)
            try:
                voted_token = tokens[top_token_index][3]
            except:
                voted_token = ''
            if is_diff_token(tokens):
                serialized_body_text_md += f'{voted_token}[^{diff_note_walker}]'
                footnote_text = self.get_footnote_text(tokens, voted_token)
                serialized_footnote_text_md += f"[^{diff_note_walker}]: {footnote_text}\n"
                diff_note_walker += 1
            else:
                if token_walker >= 100:
                    serialized_body_text_md += voted_token+"\n"
                    token_walker = 0
                else:
                    serialized_body_text_md += voted_token
            token_walker += 1
        serialized_matrix_md = f'{serialized_body_text_md}\n\n{serialized_footnote_text_md}'
        return serialized_matrix_md
    
    def save_serialized_matrix(self, serialized_matrix_md):
        output_file_path = self.output_dir / "common_spell.md"
        output_file_path.write_text(serialized_matrix_md, encoding='utf-8')
        return output_file_path