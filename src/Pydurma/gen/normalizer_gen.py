import re

from Pydurma.normalizer import Normalizer

class GenericNormalizer(Normalizer):

    def normalize_always(self, s):
        return s

    def normalize_pre_token_diff(self, s):
        s = s.lower()
        return re.sub(r"\s+$", "", s)

    def normalize_pre_token_comparison(self, s):
        s = s.lower()
        return re.sub(r"\s+$", "", s)

    def append_normalized_token_string(self, s, token_string):
        return s+token_string

