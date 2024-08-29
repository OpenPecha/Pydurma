import re
from Pydurma.bo.tokenizer_bo import TibetanTokenizer
from Pydurma.bo.normalizer_bo import TibetanNormalizer
from Pydurma.encoder import Encoder
from Pydurma.input_filters.pattern_filter import PatternInputFilter


def test_pattern_filter():
    test_string = "གི་ཚེ་རང་ཉིད༌        ཉིད་སྐྱེ་ན་རྒྱུའི། །"
    expected_string = "གི་ཚེ་རང་ཉིད་ཉིད་སྐྱེ་ན་རྒྱུའི༎ "

    filtered = PatternInputFilter(test_string, re.compile("། །"), "༎ ")
    filtered = PatternInputFilter(filtered, re.compile("༌"), "་")
    filtered = PatternInputFilter(filtered, re.compile("་ +"), "་")
    
    assert filtered.get_string() == expected_string
