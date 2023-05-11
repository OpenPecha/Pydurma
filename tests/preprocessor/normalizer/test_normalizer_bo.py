import pytest

from CommonSpell.bo.normalizer_bo import assert_conv, remove_affixes, normalize_punctuation


def test_remove_affixes():
    assert remove_affixes("དག") == "དག"
    assert remove_affixes("གའམ") == "ག"
    assert remove_affixes("དགའ") == "དགའ"
    assert remove_affixes("དགའི") == "དགའ"
    assert remove_affixes("ཀུནད") == "ཀུན"
    assert remove_affixes("འོནད") == "འོན"

@pytest.mark.skip(reason="no way of currently testing this")
def test_normalize_unicode():
    assert_conv("\u0f77", "\u0fb2\u0f71\u0f80", False)
    assert_conv("\u0f40\u0f7e\u0f7c\u0f74\u0f71", "\u0f40\u0f74\u0f71\u0f7c\u0f7e")
    assert_conv("\u0f58\u0f74\u0fb0\u0f83", "\u0f58\u0f74\u0f71\u0f83")
    assert_conv("\u0F51\u0FB7\u0F74\u0FB0", "\u0F51\u0FB7\u0F74\u0f71")
    assert_conv("\u0F66\u0F7C\u0FB1", "\u0F66\u0FB1\u0F7C")
    assert_conv("\u0F0B\u0F7E", "\u0F0B\u0F7E", False)
    assert_conv("\u0f65\u0f99\u0f7a\u0f7a", "\u0f62\u0f99\u0f7b")
    assert_conv("\u0f01\u0f83", "\u0f01\u0f83")  # should be valid

def test_normalize_punction():
    test_string = "གི་ཚེ་རང་ཉིད༌ལས་རང་        ཉིད་སྐྱེ་ན་དེའི་ཚེ་རྒྱུའི། །གཏན་ཚིགས་དང། སྡོང་བུ་ཞེས་བྱ་བ་ནི་མྱུ་གུའི་མཁྲང་བར༌འགྱུར་བའ་།། །།ཉིད་སྐྱེ་ན་དེའི་ཚེ་རྒྱུའི། །གཏན་ཚིགས་དང།། །།"
    expected_string = "གི་ཚེ་རང་ཉིད་ལས་རང་ཉིད་སྐྱེ་ན་དེའི་ཚེ་རྒྱུའི༎ གཏན་ཚིགས་དང་། སྡོང་བུ་ཞེས་བྱ་བ་ནི་མྱུ་གུའི་མཁྲང་བར་འགྱུར་བའ༎ ༎ ཉིད་སྐྱེ་ན་དེའི་ཚེ་རྒྱུའི༎ གཏན་ཚིགས་དང་༎ ༎"

    normalized_text = normalize_punctuation(test_string)
    assert expected_string == normalized_text
