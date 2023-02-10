import regex

from tokenizer import Tokenizer, TokenList, Token
from typing import List, Tuple

from vulgatizer.normalizers.normalizer import Normalizer
from vulgatizer.vocabularies.vocabulary import Vocabulary

class GenericTokenizer(Tokenizer):

    # This pattern doesn't work with the re package because of 
    # sub-optimal Unicode support. Inspired from the default pattern
    # of CollateX.

    word_punctuation_pattern = regex.compile(r"(?u)\w+\s*|\W+")

    def __init__(self, vocabulary: Vocabulary, normalizer: Normalizer, stop_words: List[str] = []):
        super().__init__(vocabulary, normalizer)
        self.stop_words = stop_words

    def tokenize(self, s: str, start=0, end: int=None) -> Tuple[str, TokenList]:
        tokens = []
        tokenstr = ""
        if end is None:
            end = len(s)
        for m in GenericTokenizer.word_punctuation_pattern.finditer(s, start, end):
            token_s = self.normalizer.normalize_always(m.group(0))
            compare_s = self.normalizer.normalize_pre_token_comparison(token_s)
            if token_s == "" or compare_s in self.stop_words:
                t: Token = (m.start(), m.end(), 0, token_s)
                tokens.append(t)
                continue
            token_s_for_diff = self.normalizer.normalize_pre_token_diff(token_s)
            code_str, code_str_len = self.vocabulary.encode_str(token_s_for_diff)
            tokenstr += code_str
            t = (m.start(), m.end(), code_str_len, token_s)
            tokens.append(t)
        return tokens, tokenstr
