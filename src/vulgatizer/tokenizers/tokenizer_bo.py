import re
import regex


from tokenizer import Tokenizer, TokenList
from typing import Tuple

from vulgatizer.normalizers.normalizer import Normalizer
from vulgatizer.normalizers.normalizer_bo import TibetanNormalizer
from vulgatizer.vocabularies.vocabulary import Vocabulary

class TibetanTokenizer(Tokenizer):

    token_pattern = regex.compile(r'(?u)\w+[\s་༌࿒]*|\W+')
    
    default_stop_words = [ "ཏུ", "གི", "ཀྱི", "གིས", "ཀྱིས", "ཡིས", 
        "ཀྱང", "སྟེ", "ཏེ", "མམ", "རམ", "སམ", "ཏམ", "ནོ", "ཏོ", "གིན",
        "ཀྱིན", "གྱིན", "ཅིང", "ཅིག", "ཅེས", "ཞེས", "པ", "པར", "པས",
        "བ", "བར", "བས", "པོ", "པོར", "པོས", "བོ", "བོར", "བོས"]

    def __init__(self, vocabulary: Vocabulary, normalizer: Normalizer, stop_words = default_stop_words):
        super().__init__(vocabulary, normalizer)
        self.stop_words = stop_words

    def tokenize(self, s: str, start=0, end: int=None) -> Tuple[str, TokenList]:
        tokens = []
        tokenstr = ""
        if end is None:
            end = len(s)
        for m in TibetanTokenizer.token_pattern.finditer(s, start, end):
            token_s = self.normalizer.normalize_always(m.group(0))
            compare_s = self.normalizer.normalize_pre_token_comparison(token_s)
            if token_s == "" or compare_s in self.stop_words:
                t = (m.start(), m.end(), 0, token_s)
                tokens.append(t)
                continue
            token_s_for_diff = self.normalizer.normalize_pre_token_diff(token_s)
            code_str, code_str_len = self.vocabulary.encode_str(token_s_for_diff)
            tokenstr += code_str
            t = (m.start(), m.end(), code_str_len, token_s)
            tokens.append(t)
        return tokens, tokenstr

if __name__ == "__main__":
    test_string = "ཡེ་ཤེས་ཀྱིས་སྦྱངས་ནས། ཆོས་ཐམས་ཅད་ནམ་མཁའི་དཀྱིལ་ལྟ་བུར་ིརང་གི་"
    vocabulary = Vocabulary()
    normalizer = TibetanNormalizer()
    tokenizer = TibetanTokenizer(vocabulary=vocabulary, normalizer=normalizer)
    tokens, tokenstr = tokenizer.tokenize(test_string, start=0, end=61)