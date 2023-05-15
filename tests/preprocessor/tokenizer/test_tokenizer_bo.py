from CommonSpell.bo.tokenizer_bo import TibetanTokenizer
from CommonSpell.bo.normalizer_bo import TibetanNormalizer
from CommonSpell.encoder import Encoder

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
    token_list, token_str = tokenizer.tokenize(test_string)
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
        

    

