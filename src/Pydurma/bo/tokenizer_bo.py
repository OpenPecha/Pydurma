import re
import regex


from typing import Tuple

from Pydurma.normalizer import Normalizer
from Pydurma.bo.normalizer_bo import TibetanNormalizer
from Pydurma.tokenizer import Tokenizer, TokenList
from Pydurma.encoder import Encoder

class TibetanTokenizer(Tokenizer):

    token_pattern = regex.compile(r'(?u)\w+[\s་༌࿒]*|\W+')
    
    # default_stop_words = [ "ཏུ", "གི", "ཀྱི", "གིས", "ཀྱིས", "ཡིས", 
    #     "ཀྱང", "སྟེ", "ཏེ", "མམ", "རམ", "སམ", "ཏམ", "ནོ", "ཏོ", "གིན",
    #     "ཀྱིན", "གྱིན", "ཅིང", "ཅིག", "ཅེས", "ཞེས", "པ", "པར", "པས",
    #     "བ", "བར", "བས", "པོ", "པོར", "པོས", "བོ", "བོར", "བོས"]

    def __init__(self, encoder: Encoder, normalizer: Normalizer):
        super().__init__(encoder, normalizer)

    def tokenize(self, arg) -> Tuple[str, TokenList]:
        tokens = []
        tokenstr = ""
        string, correct_position = self.get_input(arg)
        end = len(string)
        for m in TibetanTokenizer.token_pattern.finditer(string):
            token_s = self.normalizer.normalize_always(m.group(0))
            compare_s = self.normalizer.normalize_pre_token_comparison(token_s)
            start = correct_position(m.start())
            end = correct_position(m.end())
            if token_s == "":
                t = (start, end, 0, token_s)
                tokens.append(t)
                continue
            token_s_for_diff = self.normalizer.normalize_pre_token_diff(token_s)
            code_str, code_str_len = self.encoder.encode_str(token_s_for_diff)
            tokenstr += code_str
            t = (start, end, code_str_len, token_s)
            tokens.append(t)
        return tokenstr, tokens

if __name__ == "__main__":
    test_string = "ཡེ་ཤེས་ཀྱིས་སྦྱངས་ནས། ཆོས་ཐམས་ཅད་ནམ་མཁའི་དཀྱིལ་ལྟ་བུར་ིརང་གི་"
    encoder = Encoder()
    normalizer = TibetanNormalizer()
    tokenizer = TibetanTokenizer(encoder=encoder, normalizer=normalizer)
    tokens, tokenstr = tokenizer.tokenize(test_string, start=0, end=61)