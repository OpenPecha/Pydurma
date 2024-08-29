import re
from Pydurma.bo.tokenizer_bo import TibetanTokenizer
from Pydurma.bo.normalizer_bo import TibetanNormalizer
from Pydurma.encoder import Encoder
from Pydurma.input_filters.pattern_filter import PatternInputFilter

def test_tokenizer_bo():
    test_string = "བཀྲ་ཤིས་ཀུན་གྱི་བཀྲ་ཤིས་པ།"
    expected_token_string = '+,-.+,/0'
    expected_token_list = [
        (0, 4, 1, 'བཀྲ་'), 
        (4, 8, 1, 'ཤིས་'), 
        (8, 12, 1, 'ཀུན་'),
        (12, 16, 1, 'གྱི་'),
        (16, 20, 1, 'བཀྲ་'),
        (20, 24, 1, 'ཤིས་'),
        (24, 25, 1, 'པ'), 
        (25, 26, 1, '།')
        ]
    encoder = Encoder()
    normalizer = TibetanNormalizer()
    tokenizer = TibetanTokenizer(encoder=encoder, normalizer=normalizer)
    token_str, token_list = tokenizer.tokenize(test_string)
    assert token_list == expected_token_list
    assert token_str == expected_token_string


def test_tokenizer_with_filter():
    test_string = "གི་ཚེ་རང་ཉིད༌        ཉིད་སྐྱེ་ན་རྒྱུའི། །"
    expected_token_string = '+,-../012'
    expected_token_list = [
        (0, 3, 1, 'གི་'),
        (3, 6, 1, 'ཚེ་'),
        (6, 9, 1, 'རང་'),
        (9, 21, 1, 'ཉིད་'),
        (21, 25, 1, 'ཉིད་'),
        (25, 30, 1, 'སྐྱེ་'),
        (30, 32, 1, 'ན་'),
        (32, 38, 1, 'རྒྱུའི'),
        (38, 41, 1, '།། '),

        ]
    encoder = Encoder()
    normalizer = TibetanNormalizer()
    tokenizer = TibetanTokenizer(encoder=encoder, normalizer=normalizer)
    filtered = PatternInputFilter(test_string, re.compile("། །"), "༎ ")
    filtered = PatternInputFilter(filtered, re.compile("༌"), "་")
    filtered = PatternInputFilter(filtered, re.compile("་ +"), "་")
    token_str, token_list = tokenizer.tokenize(filtered)
    assert token_list == expected_token_list
    assert token_str == expected_token_string




# if __name__ == "__main__":
#     encoder = Encoder()
#     normalizer = TibetanNormalizer()
#     tokenizer = TibetanTokenizer(encoder=encoder, normalizer=normalizer)
    
#     test_strings = [
#         '༄༅། །རིགས་པ་བསྟན་པར་བྱ་བའི་ཕྱིར། དེ་ཉིད་ཀྱི་བཀྲ་ཤིས་ཀུན་གྱི་བཀྲ་ཤིས་པ།',
#         'རིགས་པ་བསྟན་པར་བྱ་བའི་ཕྱིར། དེ་ཉིད་ཀྱི་བཀྲ་ཤིས་ཀུད་གྱི་བཀྲ་ཤིས་པ།',
#         'རིག་པ་བསྟན་པར་དེ་ཉིད་ཀྱི་བཀྲ་ཤིས་ཀུན་ཀྱི་བཀྲ་ཤིས་པ།'
#     ]
#     for index, test_string in enumerate(test_strings, 1):
#         token_list, token_str = tokenizer.tokenize(test_string)
#         print(f'{index} {token_str}')
        

    

