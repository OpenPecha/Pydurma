import logging
import pytest

from CommonSpell.gen.tokenizer_gen import GenericTokenizer
from CommonSpell.encoder import Encoder
from CommonSpell.aligners.fdmp import FDMPaligner
from CommonSpell.gen.normalizer_gen import GenericNormalizer
from CommonSpell.utils.utils import *


#logging.basicConfig(level=logging.DEBUG)
@pytest.mark.skip(reason="no way of currently testing this")
def test_cmp_to_rows(strings):
    normalizer = GenericNormalizer()
    encoder = Encoder()
    tokenizer = GenericTokenizer(encoder, normalizer)
    token_lists = []
    token_strings = []
    for string in strings:
        tokens, tokenstr = tokenizer.tokenize(string)
        #print(encoder.decode_string(other_tokenstr))
        token_lists.append(tokens)
        token_strings.append(tokenstr)
    aligner = FDMPaligner()
    matrix = aligner.get_alignment_matrix(token_strings, token_lists)
    return column_matrix_to_row_matrix(matrix)

@pytest.mark.skip(reason="no way of currently testing this")
def test_rows(strings, expected_rows):
    rows = test_cmp_to_rows(strings)
    for i, row in enumerate(rows):
        text_row = token_row_to_text_row(row, strings[i])
        assert(text_row == expected_rows[i])

@pytest.mark.skip(reason="no way of currently testing this")
def test_simple():
    strings = []
    strings.append("The quick brown fox jumped over the lazy dog.")
    strings.append("The brown fox jumped over the very lazy dog.")
    expected = [
        ['The ', 'quick ', 'brown ', 'fox ', 'jumped ', 'over ', 'the ', '-', 'lazy ', 'dog', '.'],
        ['The ', '-', 'brown ', 'fox ', 'jumped ', 'over ', 'the ', 'very ', 'lazy ', 'dog', '.']
    ]
    test_rows(strings, expected)
    strings = []
    strings.append("quick brown fox jumped over the lazy dog.")
    strings.append("The quick brown fox jumped over the very lazy dog.")
    expected = [
        ['-', 'quick ', 'brown ', 'fox ', 'jumped ', 'over ', 'the ', '-', 'lazy ', 'dog', '.'],
        ['The ', 'quick ', 'brown ', 'fox ', 'jumped ', 'over ', 'the ', 'very ', 'lazy ', 'dog', '.']
    ]
    test_rows(strings, expected)
    strings = []
    strings.append("the fast")
    strings.append("the quick")
    expected = [
        ['the ', 'fast'],
        ['the ', 'quick']
    ]
    test_rows(strings, expected)
    strings = []
    strings.append("the")
    strings.append("the quick")
    expected = [
        ['the', '-'],
        ['the ', 'quick']
    ]
    test_rows(strings, expected)
    strings = []
    strings.append("and")
    strings.append("and the quick")
    expected = [
        ['and', '-', '-'],
        ['and ', 'the ', 'quick']
    ]
    # test_rows(strings, expected, ["the"])
    # test zero-increment tokens aligned in the middle
    strings = []
    strings.append("over the lazy")
    strings.append("over the lazy")
    expected = [
        ['over ', 'the ', 'lazy'],
        ['over ', 'the ', 'lazy']
    ]
    # test_rows(strings, expected, ["the"])
    # test zero-increment token at the end of the first string
    strings = []
    strings.append("over lazy the")
    strings.append("over the lazy")
    expected = [
        ['over ', '-', 'lazy ', 'the'],
        ['over ', 'the ', 'lazy', '-']
    ]
    # test_rows(strings, expected, ["the"])
    # test zero-increment token at the end of the second string
    strings = []
    strings.append("over the lazy")
    strings.append("over lazy the")
    expected = [
        ['over ', 'the ', 'lazy', '-'],
        ['over ', '-', 'lazy ', 'the']
    ]
    # test_rows(strings, expected, ["the"])

@pytest.mark.skip(reason="no way of currently testing this")
def test_complex():
    aligner = FDMPaligner()
    token_strings = {
        'V1':"ABC",
        'V2': "AC"
    } 
    token_lists = {
        'V1': [(0,1,2,"AB"), (1,2,1,"C")],
        'V2': [(0,1,1,"A"), (1,2,1,"C")]
    }
        
    matrix = aligner.get_alignment_matrix(token_strings, token_lists)
    row_matrix = column_matrix_to_row_matrix(matrix)
    expected_row_matrix = [
        [(0,1,2,"AB"), (1,2,1,"C")],
        [(0,1,1,"A"), (1,2,1,"C")]
    ]
    assert(row_matrix == expected_row_matrix)

# test_simple()
#test_complex()

