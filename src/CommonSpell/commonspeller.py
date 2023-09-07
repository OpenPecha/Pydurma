from pathlib import Path

from CommonSpell.aligners.aligner import Aligner
from CommonSpell.input_filters.pattern_filter import PatternInputFilter
from CommonSpell.tokenizer import Tokenizer

class CommonSpeller():

    def __init__(self, aligner: Aligner, filter_patterns: list[tuple], tokenizer: Tokenizer, version_paths: list, examplar_version_path: Path):
        self.aligner = aligner
        self.filter_patterns = filter_patterns
        self.tokenizer = tokenizer
        self.version_paths = version_paths
        self.version_paths.sort()
        self.examplar_version_path = examplar_version_path
        

    
    def add_version_paths(self, version_path: Path):
        self.version_paths.append(version_path)

    def add_version(self, version_path: Path):
        version_text = version_path.read_text(encoding='utf-8')
        version_text = version_text.replace('། ་', '། །')
        for filter_pattern in self.filter_patterns:
            version_text = PatternInputFilter(version_text, filter_pattern[0], filter_pattern[1])
        
        token_string, token_list = self.tokenizer.tokenize(version_text)
        return token_string, token_list

    def preprocess_versions(self):
        token_strings = []
        token_lists = []
        token_string, token_list = self.add_version(self.examplar_version_path)
        token_strings.append(token_string)
        token_lists.append(token_list)
        for version_path in self.version_paths:
            token_string, token_list = self.add_version(version_path)
            token_strings.append(token_string)
            token_lists.append(token_list)
        return token_strings, token_lists


    def get_common_spell_matrix(self):
        token_strings, token_lists = self.preprocess_versions()
        token_matrix = self.aligner.get_alignment_matrix(token_strings, token_lists)
        return token_matrix
