import re
import regex


from typing import Tuple

from CommonSpell.normalizer import Normalizer
from CommonSpell.bo.normalizer_bo import TibetanNormalizer, normalize_punctuation
from CommonSpell.tokenizer import Tokenizer, TokenList
from CommonSpell.encoder import Encoder

class TibetanTokenizer(Tokenizer):

    token_pattern = regex.compile(r'(?u)\w+[\s་༌࿒]*|\W+')
    
    # default_stop_words = [ "ཏུ", "གི", "ཀྱི", "གིས", "ཀྱིས", "ཡིས", 
    #     "ཀྱང", "སྟེ", "ཏེ", "མམ", "རམ", "སམ", "ཏམ", "ནོ", "ཏོ", "གིན",
    #     "ཀྱིན", "གྱིན", "ཅིང", "ཅིག", "ཅེས", "ཞེས", "པ", "པར", "པས",
    #     "བ", "བར", "བས", "པོ", "པོར", "པོས", "བོ", "བོར", "བོས"]

    def __init__(self, encoder: Encoder, normalizer: Normalizer):
        super().__init__(encoder, normalizer)

    def tokenize(self, s: str, start=0, end: int=None) -> Tuple[str, TokenList]:
        tokens = []
        tokenstr = ""
        s = normalize_punctuation(s)
        if end is None:
            end = len(s)
        for m in TibetanTokenizer.token_pattern.finditer(s, start, end):
            token_s = self.normalizer.normalize_always(m.group(0))
            # compare_s = self.normalizer.normalize_pre_token_comparison(token_s)
            if token_s == "":
                t = (m.start(), m.end(), 0, token_s)
                tokens.append(t)
                continue
            token_s_for_diff = self.normalizer.normalize_pre_token_diff(token_s)
            code_str, code_str_len = self.encoder.encode_str(token_s_for_diff)
            tokenstr += code_str
            t = (m.start(), m.end(), code_str_len, token_s)
            tokens.append(t)
        return tokens, tokenstr

if __name__ == "__main__":
    test_string = "ཡེ་ཤེས་ཀྱིས་སྦྱངས་ནས། ཆོས་ཐམས་ཅད་ནམ་མཁའི་དཀྱིལ་ལྟ་བུར་ིརང་གི་"
    encoder = Encoder()
    normalizer = TibetanNormalizer()
    tokenizer = TibetanTokenizer(encoder=encoder, normalizer=normalizer)
    tokens, tokenstr = tokenizer.tokenize(test_string, start=0, end=61)