from pathlib import Path

from CommonSpell.aligners.aligner import Aligner
from CommonSpell.tokenizer import Tokenizer

class CommonSpeller():

    def __init__(self, aligner: Aligner, tokenizer: Tokenizer, version_paths) -> None:
        self.aligner = aligner
        self.tokenizer = tokenizer
        self.version_paths = version_paths

    
    def add_versions(self, version_path: Path):
        self.version_paths.append(version_path)

    def preprocess_versions(self):
        token_strings = []
        token_lists = []
        for version_path in self.version_paths:
            version_text = version_path.read_text(encoding='utf-8')
            version_text = version_text.replace("\n", "")
            token_list, token_string = self.tokenizer.tokenize(version_text)
            token_strings.append(token_string)
            token_lists.append(token_list)
        return token_strings, token_lists


    def get_common_spell_matrix(self):
        token_strings, token_lists = self.preprocess_versions()
        token_matrix = self.aligner.get_alignment_matrix(token_strings, token_lists)
        return token_matrix
