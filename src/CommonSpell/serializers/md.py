from pathlib import Path
from typing import List

from CommonSpell.aligners.aligner import TokenMatrix
from CommonSpell.serializers.serializer import Serializer
from CommonSpell.weighers.matrix_weigher import WeightMatrix
from CommonSpell.utils.utils import is_diff_token, get_token_strings, get_top_weight_index



class MdSerializer(Serializer):

    def __init__(self, weighted_token_matrix: TokenMatrix, output_dir: Path) -> None:
        super().__init__(weighted_token_matrix, output_dir)

    def regroup_same_diffs(self, diff_tokens):
        regrouped_notes = {}
        for version_name, diff_string in diff_tokens.items():
            regrouped_notes[diff_string] = [version_name] if diff_string not in regrouped_notes.keys() else regrouped_notes[diff_string] + [version_name]
        return regrouped_notes

    def get_footnote_text(self, diff_tokens, voted_token):
        note_text = f'{voted_token}]'
        diff_token_strings = get_token_strings(diff_tokens)
        regrouped_notes = self.regroup_same_diffs(diff_token_strings)
        for diff_string, verions in regrouped_notes.items():
            version_names = ','.join(verions)
            note_text += f"{version_names}: {diff_string}; "
        return note_text[:-1]
        
    def serialize_matrix(self):
        diff_note_walker = 1
        serialized_body_text_md = ''
        serialized_footnote_text_md = ''
        serialized_matrix_md = ''
        for tokens_info in self.weighted_token_matrix:
            top_token_index = get_top_weight_index(tokens_info)
            try:
                voted_token = tokens_info[top_token_index][3]
            except:
                voted_token = ''
            if is_diff_token(tokens_info):
                serialized_body_text_md += f'{voted_token}[^{diff_note_walker}]'
                footnote_text = self.get_footnote_text(tokens_info, voted_token)
                serialized_footnote_text_md += f"[^{diff_note_walker}]: {footnote_text}\n"
                diff_note_walker += 1
            else:
                serialized_body_text_md += voted_token
        serialized_matrix_md = f'{serialized_body_text_md}\n\n{serialized_footnote_text_md}'
        return serialized_matrix_md
    
    def save_serialized_matrix(self, serialized_matrix_md):
        output_file_path = self.output_dir / "common_spell.md"
        output_file_path.write_text(serialized_matrix_md, encoding='utf-8')
        return output_file_path