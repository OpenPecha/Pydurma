import re
from pathlib import Path
from typing import List

from Pydurma.aligners.aligner import TokenMatrix
from Pydurma.serializers.serializer import Serializer
from Pydurma.weighers.matrix_weigher import WeightMatrix
from Pydurma.utils.utils import is_diff_token, get_token_strings, get_top_weight_index



class HFMLSerializer(Serializer):

    def __init__(self, 
                 weighted_token_matrix: TokenMatrix, 
                 output_dir: Path, 
                 text_id:str,
                 version_paths: List[Path],
                 verions_to_serialize: List[str]) -> None:
        self.weighted_token_matrix = weighted_token_matrix
        self.output_dir = output_dir
        self.text_id = text_id
        self.version_paths = version_paths
        self.version_paths.sort()
        self.versions_to_serialize = verions_to_serialize

    def regroup_same_diffs(self, diff_tokens):
        regrouped_notes = {}
        for version_name, diff_string in diff_tokens.items():
            regrouped_notes[diff_string] = [version_name] if diff_string not in regrouped_notes.keys() else regrouped_notes[diff_string] + [version_name]
        return regrouped_notes

    def filter_versions_to_serialize(self, diff_token_strings, versions_to_serialize):
        filtered_diff_token_strings = {}
        if not versions_to_serialize:
            for version_index, (version_name, diff_string) in enumerate(diff_token_strings.items(), 1):
                filtered_diff_token_strings[f'V{version_index}'] = diff_string
        for version_name, diff_string in diff_token_strings.items():
            if version_name in versions_to_serialize:
                version_code = versions_to_serialize.get(version_name)
                filtered_diff_token_strings[version_code] = diff_string
        return filtered_diff_token_strings

    def get_footnote_text(self, diff_tokens, voted_token):
        note_text = f'<'
        diff_token_strings = get_token_strings(diff_tokens, self.version_paths)
        diff_token_strings = self.filter_versions_to_serialize(diff_token_strings, self.versions_to_serialize)
        regrouped_notes = self.regroup_same_diffs(diff_token_strings)
        for diff_string, verions in regrouped_notes.items():
            if diff_string == voted_token:
                continue
            version_names = ''.join(verions)
            note_text += f"{version_names}{diff_string}"
        return f'{note_text}>'

    def is_single_syl_note(self, voted_token):
        syls = re.split('་', voted_token)
        syls = [syl for syl in syls if syl]
        if len(syls) == 1:
            return True
        return False
        
    def serialize_matrix(self):
        diff_note_walker = 1
        serialized_hfml = ''
        for tokens_info in self.weighted_token_matrix:
            top_token_index = get_top_weight_index(tokens_info)
            try:
                voted_token = tokens_info[top_token_index][3]
            except:
                voted_token = ''
            if is_diff_token(tokens_info):
                footnote_text = self.get_footnote_text(tokens_info, voted_token)
                if footnote_text != '<>':
                    if self.is_single_syl_note(voted_token):
                        serialized_hfml += f'{voted_token}({diff_note_walker}) {footnote_text}'
                    else:
                        serialized_hfml += f':{voted_token}({diff_note_walker}) {footnote_text}'
                    diff_note_walker += 1
                else:
                    serialized_hfml += voted_token
            else:
                serialized_hfml += voted_token
        return serialized_hfml
    
    def save_serialized_matrix(self, serialized_matrix_md):
        output_file_path = self.output_dir / f"{self.text_id}_hfml.txt"
        output_file_path.write_text(serialized_matrix_md, encoding='utf-8')
        return output_file_path