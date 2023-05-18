import re
from CommonSpell.bo.tokenizer_bo import TibetanTokenizer
from CommonSpell.bo.normalizer_bo import TibetanNormalizer
from CommonSpell.encoder import Encoder
from CommonSpell.input_filters.pattern_filter import PatternInputFilter


def test_pattern_filter():
    test_string = "གི་ཚེ་རང་ཉིད༌        ཉིད་སྐྱེ་ན་རྒྱུའི། །"
    expected_string = "གི་ཚེ་རང་ཉིད་ཉིད་སྐྱེ་ན་རྒྱུའི༎ "

    filtered = PatternInputFilter(test_string, re.compile("། །"), "༎ ")
    filtered = PatternInputFilter(filtered, re.compile("༌"), "་")
    filtered = PatternInputFilter(filtered, re.compile("་ +"), "་")
    
    assert filtered.get_string() == expected_string
