import re

from enum import Enum

from vulgatizer import config
from vulgatizer.normalizer import Normalizer


class Cats(Enum):
    Other = 0
    Base = 1
    Subscript = 2
    BottomVowel = 3
    BottomMark = 4
    TopVowel = 5
    TopMark = 6
    RightMark = 7

CATEGORIES =  ([Cats.Other]           # 0F00
             + [Cats.Base]            # 0F01, often followed by 0f083
             + [Cats.Other] * 22      # 0F02-0F17
             + [Cats.BottomVowel] * 2 # 0F18-0F19
             + [Cats.Other] * 6       # 0F1A-0F1F
             + [Cats.Base] * 20       # 0F20-0F33, numbers can be followed by 0f18, 0f19 or exceptionally by vowels
             + [Cats.Other]           # 0F34
             + [Cats.BottomMark]      # 0F35
             + [Cats.Other]           # 0F36
             + [Cats.BottomMark]      # OF37
             + [Cats.Other]           # 0F38
             + [Cats.Subscript]       # 0F39, kind of cheating but works
             + [Cats.Other] * 4       # 0F3A-0F3D
             + [Cats.RightMark]       # 0F3E
             + [Cats.Other]           # 0F3F, not quite sure
             + [Cats.Base] * 45       # 0F40-0F6C
             + [Cats.Other] * 4       # 0F6D-0F70
             + [Cats.BottomVowel]     # 0F71
             + [Cats.TopVowel]        # 0F72
             + [Cats.TopVowel]        # 0F73
             + [Cats.BottomVowel] * 2 # 0F74-0F75
             + [Cats.TopVowel] * 8    # 0F76-0F7D
             + [Cats.TopMark]         # 0F7E
             + [Cats.RightMark]       # 0F7F
             + [Cats.TopVowel] * 2    # 0F80-0F81
             + [Cats.TopMark] * 2     # 0F82-0F83
             + [Cats.BottomMark]      # 0F84
             + [Cats.Other]           # 0F85
             + [Cats.TopMark] * 2     # 0F86-0F87
             + [Cats.Base] * 2        # 0F88-0F89
             + [Cats.Base]            # 0F8A always followed by 0f82 (required by the Unicode spec)
             + [Cats.Other]           # 0F8B
             + [Cats.Base]            # 0F8C
             + [Cats.Subscript] * 48  # 0F8D-0FBC
             )

def charcat(c):
    ''' Returns the category for a single char string'''
    o = ord(c)
    if 0x0F00 <= o <= 0x0FBC:
        return CATEGORIES[o-0x0F00]
    return Cats.Other

# debug:
#for i, c in enumerate(CATEGORIES):
#    print("%x : %d" % (0x0F00 + i , c.value))

def unicode_reorder(txt):
    # case of a syllable starting with a diacritic (ex: a vowel or subscript)
    # we push it after the first main letter
    # txt = re.sub(r"^([\u0f71-\u0f84\u0f8d-\u0fbc]+)([\u0f40-\u0f6c])", r"\2", txt)
    # return txt, True
    # inpired from code for Khmer Unicode provided by SIL
    # https://docs.microsoft.com/en-us/typography/script-development/tibetan#reor
    # https://docs.microsoft.com/en-us/typography/script-development/use#glyph-reordering
    charcats = [charcat(c) for c in txt]
    # find subranges of base+non other and sort components in the subrange
    i = 0
    res = []
    valid = True
    while i < len(charcats):
        c = charcats[i]
        if c != Cats.Base:
            if c.value > Cats.Base.value:
                valid = False
            res.append(txt[i])
            i += 1
            continue
        # scan for end of component
        j = i + 1
        while j < len(charcats) and charcats[j].value > Cats.Base.value:
            j += 1
        # sort syllable based on character categories
        # sort the char indices by category then position in string
        newindices = sorted(range(i, j), key=lambda e:(charcats[e].value, e))
        replaces = "".join(txt[n] for n in newindices)
        res.append(replaces)
        i = j
    return "".join(res), valid

def normalize_unicode(s, form="nfd"):
    # first, unify Unicode form:
    # http://www.unicode.org/faq/normalization.html
    # https://unicode.org/reports/tr15/
    # https://unicode.org/charts/normalization/chart_Tibetan.html
    # although for some reason this chart considers 0f0c -> 0f0b in NFD
    #
    # deprecated or discouraged characters
    s = s.replace("\u0f73", "\u0f71\u0f72") # use is discouraged
    s = s.replace("\u0f75", "\u0f71\u0f74") # use is discouraged
    s = s.replace("\u0f77", "\u0fb2\u0f71\u0f80") # deprecated
    s = s.replace("\u0f79", "\u0fb3\u0f71\u0f80") # deprecated
    s = s.replace("\u0f81", "\u0f71\u0f80") # use is discouraged
    if form == "nfd":
        s = s.replace("\u0f43", "\u0f42\u0fb7")
        s = s.replace("\u0f4d", "\u0f4c\u0fb7")
        s = s.replace("\u0f52", "\u0f51\u0fb7")
        s = s.replace("\u0f57", "\u0f56\u0fb7")
        s = s.replace("\u0f5c", "\u0f5b\u0fb7")
        s = s.replace("\u0f69", "\u0f40\u0fb5")
        s = s.replace("\u0f76", "\u0fb2\u0f80")
        s = s.replace("\u0f78", "\u0fb3\u0f80")
        s = s.replace("\u0f93", "\u0f92\u0fb7")
        s = s.replace("\u0f9d", "\u0f9c\u0fb7")
        s = s.replace("\u0fa2", "\u0fa1\u0fb7")
        s = s.replace("\u0fa7", "\u0fa6\u0fb7")
        s = s.replace("\u0fac", "\u0fab\u0fb7")
        s = s.replace("\u0fb9", "\u0f90\u0fb5")
    else:
        s = s.replace("\u0f42\u0fb7", "\u0f43")
        s = s.replace("\u0f4c\u0fb7", "\u0f4d")
        s = s.replace("\u0f51\u0fb7", "\u0f52")
        s = s.replace("\u0f56\u0fb7", "\u0f57")
        s = s.replace("\u0f5b\u0fb7", "\u0f5c")
        s = s.replace("\u0f40\u0fb5", "\u0f69")
        s = s.replace("\u0fb2\u0f80", "\u0f76")
        s = s.replace("\u0fb3\u0f80", "\u0f78")
        s = s.replace("\u0f92\u0fb7", "\u0f93")
        s = s.replace("\u0f9c\u0fb7", "\u0f9d")
        s = s.replace("\u0fa1\u0fb7", "\u0fa2")
        s = s.replace("\u0fa6\u0fb7", "\u0fa7")
        s = s.replace("\u0fab\u0fb7", "\u0fac")
        s = s.replace("\u0f90\u0fb5", "\u0fb9")
    # 0f00 has not been marked as a composed character in Unicode
    # This is something that is now seen as a mistake, but it cannot be
    # changed because of Unicode change policies.
    s = s.replace("\u0f00", "\u0f68\u0f7c\u0f7e")
    # ra does't transform into a small rago before nya or la, so using 0f65
    # does not change its graphical representation in that case
    s = s.replace("\u0f65\u0f99", "\u0f62\u0f99")
    s = s.replace("\u0f65\u0fb3", "\u0f62\u0fb3")
    s, valid = unicode_reorder(s)
    s = normalize_invalid_start_tokens(s)
    return s, valid

def normalize_graphical(s):
    """
    These substitutions normalize things that have the same
    graphical representation
    """
    # no graphical distinction between 0f0b and 0f0c
    s = s.replace("\u0f0c", "\u0f0b")
    # double shad is just two shad
    s = s.replace("\u0f0e", "\u0f0d\u0f0d")
    # the distinction between 0f38 and 0f27 is semantic but rarely
    # distinguished graphically and often completely missed by inputters
    s = s.replace("\u0f38", "\u0f27")
    # /!\ some fonts don't display these combinations in the exact same way
    # but since there's no semantic distinction and the graphical variation
    # is unclear, it seems safe
    s = s.replace("\u0f7a\u0f7a", "\u0f7b")
    s = s.replace("\u0f7c\u0f7c", "\u0f7d")
    # the diference between 0f71 and 0fb0 is often very ambiguous when
    # looking at original sources. We normalize them in order to
    # make the data coherent:
    # no 0f71 in the middle of stacks, only 0fb0
    s = re.sub(r"[\u0f71]([\u0f8d-\u0fac\u0fae\u0fb0\u0fb3-\u0fbc])", "\u0fb0\\1", s)
    # no 0fb0 at the end of stacks, only 0f71
    s = re.sub(r"[\u0fb0]([^\u0f8d-\u0fac\u0fae\u0fb0\u0fb3-\u0fbc]|$)", "\u0f71\\1", s)
    # things we do not normalize:
    # 0f74+0f71 -> 0f71+0f74, because the combination appears sometimes in the sources
    # for instance སུྰ in https://adarsha.dharma-treasure.org/kdbs/jiangkangyur/pbs/2618229
    # same for 0fb1+0f71 since the combination also appears
    # for instance སཱྱ on https://adarsha.dharma-treasure.org/kdbs/jiangkangyur?pbId=2627013
    return s

def normalize_punctuation(s, use_gter_shad=False, original_eol=True):
    # normalize spaces
    s = re.sub(r"\s+", " ", s)
    # both are done in the usual normalization
    # no graphical distinction between 0f0b and 0f0c
    #s = s.replace("\u0f0c", "\u0f0b")
    # double shad is just two shad
    #s = s.replace("\u0f0e", "\u0f0d\u0f0d")
    # we don't want to keep double tshegs (I suppose)
    s = s.replace("\u0fd2", "\u0f0b")
    # normalize end of line characters
    s = re.sub(r"(?:\r\n|\n)", "\n", s)
    if not original_eol:
        # 0f11 is just a normal shad that appears in some cases at the beginning of a page,
        # mostly when there is just one syllable before the shad on the first line, but it
        # has no semantic significance, it should be turned into a normal shad when combining
        # multiple texts
        s = s.replace("\u0f11", "\u0f0d")
        # remove all yig mgo: 0f01+diacritic?, 0f02-0f07, 0fd0-0fd1, 0fd3-0fd4
        # as well as their surrounding punctuation: space, 0f0d-0f11, 0f14
        s = re.sub(r"[ \u0f0d-\u0f11\u0f14]*[\u0f01-\u0f07\u0fd0\u0fd1\u0fd3\u0fd4]+[ \u0f0d-\u0f11\u0f14\u0f71-\u0f87]*", "", s)
        # remove all punctuation at beginning of line
        s = re.sub(r"(^|[\n])[\u0f0b-\u0f14]+", "\\1", s)
        # ensure tsheg at end of line after normal letters, except after ཀ, ག and ཤ
        # (where the absence of a tsheg should be interpreted as the presence of a shad)
        s = re.sub(r"([\u0f41\u0f43-\u0f63\u0f65-\u0f6c][\u0f71-\u0fbc]*) *($|[\n])", "\\1\u0f0b\\2", s)
        # ensure space after ཀ, ག and ཤ at end of line so that it merges well with the following one
        # remove line breaks and spaces at beginning of lines
        s = re.sub(r"([ཀགཤ][\u0f71-\u0f87]*)\n", "\\1 \n", s)
        s = re.sub(r"(?:\n) *", "", s)
    s = s.replace("\u0f14", "\u0f0d")
    # replace shads with surrounding spaces by a simple shad with a space after
    s = re.sub(r"[ \u0f0d]+", "\u0f0d ", s)
    # tshegs are sometimes used as padding, no need to keep it
    s = re.sub(r"[\u0f0b][\u0f0b]+", "\u0f0b", s)
    # remove tshegs before punctuation, including shad (no tsheg before gter shad)
    s = re.sub(r"[\u0f0b]([\u0f0d-\u0f14])", "\\1", s)
    # ensure space after shad
    s = re.sub(r"[\u0f0d]([^ ])", "\u0f0d \\1", s)
    # no tsheg after visarga
    s = s.replace("\u0f7f\u0f0b", "\u0f7f")
    if use_gter_shad:
        s = s.replace("\u0f0d", "\u0f14")
    else:
        # add tshegs before shad in some circumstances (after ང)
        s = re.sub(r"(ང[\u0f71-\u0f87]*)[\u0f0d]", "\\1\u0f0b\u0f0d", s)
        # remove shad after ཀ, ག and ཤ
        s = re.sub(r"([ཀགཤ][\u0f71-\u0f87]*)[\u0f0d]", "\\1", s)
    # normalize non-Tibetan punctuation into Chinese punctuation or Western punctuation (option?)
    # 〈〈?, 〈〈, 《, «, 〉〉?, », 》, 〉〉, ( ), ;, comma, dot, etc.
    # TODO
    # remove spaces: NO_SPACE_AFTER_PATTERN = re.compile(r"(?:\s|[༌་])$")
    # TODO
    return s

def normalize_punctuation_token_always(s, keep_eol=True):
    """
    Here we assume we have a token that comes out of the TibetanTokenizer
    """
    # normalize spaces
    if keep_eol:
        # normalize spaces (except new lines)
        s = re.sub(r"[^\S\r\n]+", " ", s)
        # normalize new line characters
        s = s.replace("\r\n", "\n")
    else:
        # remove all yig mgo: 0f01+diacritic?, 0f02-0f07, 0fd0-0fd1, 0fd3-0fd4
        # as well as their surrounding punctuation: space, 0f0d-0f11, 0f14
        s = re.sub(r"[ \u0f0d-\u0f11\u0f14]*[\u0f01-\u0f07\u0fd0\u0fd1\u0fd3\u0fd4]+[ \u0f0d-\u0f11\u0f14\u0f71-\u0f87]*", "", s)
        # ensure space after ཀ, ག and ཤ at end of line so that it merges well with the following one
        # remove line breaks and spaces at beginning of lines
        s = re.sub(r"([ཀགཤ][\u0f71-\u0f87]*)\n", r"\1 ", s)
        # remove new line + all punctuation at beginning of line
        s = re.sub(r"(?:^|\n|\r\n)[\u0f0b-\u0f14\s]+", "", s)
        # normalize spaces
        s = re.sub(r"\s+", " ", s)
        # since the token comes from the tokenizer, normal tshegs are merges with the previous token
        # so the tshegs in the strings typically come from padding at the end of a line, which we want
        # to remove if we don't keep the end of lines
        s = s.replace("\u0f0b", "")
        # 0f11 is just a normal shad that appears in some cases at the beginning of a page,
        # mostly when there is just one syllable before the shad on the first line, but it
        # has no semantic significance, it should be turned into a normal shad when combining
        # multiple texts
        s = s.replace("\u0f11", "\u0f0d")
    # normalization of 0f0c and 0f0e are done through the usual normalization
    # replace shads with surrounding spaces by a simple shad with a space after
    s = re.sub(r"( *[\u0f0d] *)+", "\u0f0d ", s)
    return s

def normalize_punctuation_token_pre_token_diff(s, keep_eol=True):
    # fold different types of shad into regular shad
    s = re.sub(r"[\u0f0f-\u0f14]", "\u0f0d", s)
    s = s.replace("\u0fd2", "\u0f0b")
    s = s.replace("\n", "")
    return s


def normalize_unusual(s):
    #
    # some symbols are not doubled outside of exceptional shorthands. See
    # A Handbook of Abbreviations by the Dzongkha Development Commission:
    # https://www.dzongkha.gov.bt/uploads/files/publications/A_handbook_of_Dzongkha_and_Ch%C3%B6k%C3%A9_abbreviations_e78335551931b7bb0ea4666213f57824.pdf
    # these characters are 0f71-0f87, 0f35, 0f37, 0f39 0fad, 0fb1 and 0fb2
    # TODO
    #
    # tsheg + vowel should be vowel + tsheg in most cases, although this
    # heuristic can fail
    # TODO
    #
    # remove tsheg and diacritics at beginning of lines
    # TODO
    return s

def debug_to_unicode(s):
    res = ""
    for c in s:
        res += "\\u%x " % ord(c)
    return res

def assert_conv(orig, expected, expectedValid = True):
    resultStr, resultValid = normalize_unicode(orig)
    assert resultStr == expected, "%s -> %s but %s expected" % (debug_to_unicode(orig), debug_to_unicode(resultStr), debug_to_unicode(expected))
    assert resultValid == expectedValid, "%s valid? -> %s but %s expected" % (debug_to_unicode(orig), resultValid, expectedValid)


# Normalization of Old Tibetan shorthands

# from Tibetan-nlp: Traditionally in Classical Tibetan, syllables are separated by a tsheg. 
# In Old Tibetan texts, syllable margins are not so clear and often a syllable (verb, noun and so on)
# is merged together with the following case marker or converb (For example: སྟགི > སྟག་གི,  དུསུ > དུས་སུ,  བཀུམོ > བཀུམ་མོ). 
# Rule: Split merged syllables for cases as དྲངསྟེ > དྲངས་ཏེ
#  ([ཀ-ྼ])སྟེ   -> $1ས་
OLD_TIB_P1 = re.compile(r"([ཀ-ྼ])སྟེ")

# from Tibetan-nlp:
# Rule: Split merged syllables for cases as གཅལྟོ > གཅལད་ཏོ
# ([ཀ-ྼ][ནལར])ྟ([ེོ])", "$1་ཏ$2
OLD_TIB_P2 = re.compile(r"([ཀ-ྼ][ནལར])ྟ([ེོ])")

# from Tibetan-nlp:
# Rule: Split merged syllables for cases with genitive as གགྀ་ > གག་གྀ་, པགི་ > པག་གི་
# (I need to include this rule otherwise these cases are not taken into account by the
# generic rules where the condition {2-6}C will skip them.
# On the other hand, in the generic rule, using a condition as {1-6}C
# will introduce errors since the rule will split words as "bshi"
# ([ཀ-ྼ])ག([ིྀ][^ཀ-ྼ])", "$1ག་ག$2
# the first character shouldn't be a valid prefix of ག  (which are ད, བ, མ and འ), see
# https://github.com/tibetan-nlp/tibcg3/issues/4
OLD_TIB_P3 = re.compile(r"([ཀ-ཐདྷ-ཕབྷཙ-ཟཡ-ྼ])ག([ིྀ][^ཀ-ྼ])")

# from Tibetan-nlp:
# Rule: Split merged syllables
# see also https://github.com/tibetan-nlp/tibcg3/issues/6
OLD_TIB_P4 = re.compile(r"([ཀ-ྼ][ཀ-ྼ]+)([ཀ-ཟཡ-ཬ])([ོེིྀུ])")

def normalize_old_tib(s):
    """
    Normalizes Old Tibetan strings into classical Tibetan
    /! should be applied before tokenization as it introduces tshegs 
    """
    s = OLD_TIB_P1.sub(r"\1ས་ཏེ", s)
    s = OLD_TIB_P2.sub(r"\1་ཏ\2", s)
    s = OLD_TIB_P3.sub(r"\1ག་ག\2", s)
    s = OLD_TIB_P4.sub(r"\1\2་\2\3", s)
    s = s.replace("ོེ", "ོའི")
    s = s.replace("བགྱིསྣ", "བགྱིས་ན")
    s = s.replace("རབལ", "རབ་ལ")
    s = s.replace("མཆིསྣ", "མཆིས་ན")
    # s = s.replace("མོལ", "མོ་ལ") indicated in the doc, but would conflict with other things
    s = s.replace("ཐོགསླ", "ཐོག་སླ")
    s = s.replace("ལྕེབསའོ", "ལྕེབས་སོ")
    s = s.replace("གཤེགསའོ", "གཤེགས་སོ")
    s = s.replace("བཏགསའོ", "བཏགས་སོ")
    s = s.replace("ལསྩོགསྟེ", "ལ་སྩོགས་སྟེ")
    # builder.add("མའང", "མ་འང") indicated but more or less useless
    s = s.replace("མྱི", "མི")
    s = s.replace("མྱེ", "མེ")
    s = s.replace("གསྩན", "གསན")
    s = s.replace("གསྩང", "གསང")
    s = s.replace("སྩོགས", "སོགས")
    s = s.replace("སྩུབ", "སུབ")
    s = s.replace("སྩང", "སང")
    s = s.replace("སྩངས", "སངས")
    s = s.replace("གསྩུག", "གསུག")
    s = s.replace("བསྩག", "བསག")
    s = s.replace("མཀ", "མཁ")
    s = s.replace("མཅ", "མཆ")
    s = s.replace("མཏ", "མཐ")
    s = s.replace("མཙ", "མཚ")
    s = s.replace("འཀ", "འཁ")
    s = s.replace("འཅ", "འཆ")
    s = s.replace("འཏ", "འཐ")
    s = s.replace("འཔ", "འཕ")
    s = s.replace("འཙ", "འཚ")
    s = s.replace("དཁ", "དཀ")
    s = s.replace("དཕ", "དཔ")
    s = s.replace("གཆ", "གཅ")
    s = s.replace("གཐ", "གཏ")
    s = s.replace("གཚ", "གཙ")
    s = s.replace("བཁ", "བཀ")
    s = s.replace("བཆ", "བཅ")
    s = s.replace("བཐ", "བཏ")
    s = s.replace("བཚ", "བཙ")
    s = s.replace("སྑ", "སྐ")
    s = s.replace("སྠ", "སྟ")
    s = s.replace("སྥ", "སྤ")
    s = s.replace("སྪ", "སྩ")
    s = s.replace("རྑ", "རྐ")
    s = s.replace("རྪ", "རྩ")
    s = s.replace("རྠ", "རྟ")
    s = s.replace("ལྑ", "ལྐ")
    s = s.replace("ལྖ", "ལྕ")
    s = s.replace("ལྠ", "ལྟ")
    s = s.replace("ལྥ", "ལྤ")
    s = s.replace("པྱག", "ཕྱག")
    s = s.replace("པྱི", "ཕྱི")
    s = s.replace("པོ་ཉ", "ཕོ་ཉ")
    s = s.replace("དམག་ཕོན", "དམག་དཔོན")
    s = s.replace("པོག་པ", "ཕོག་པ")
    s = s.replace("ཕོ་བྲང", "པོ་བྲང")
    s = s.replace("བལ་ཕོ", "བལ་པོ")
    s = s.replace("ཕལ་ཕོ", "ཕལ་པོ")
    s = s.replace("རྩང་ཅེན", "རྩང་ཆེན")
    s = s.replace("ལོ་ཕར", "ལོ་པར")
    s = s.replace("བློན་ཅེ", "བློན་ཆེ")
    s = s.replace("ཞལ་ཅེ", "ཞལ་ཆེ")
    s = s.replace("མེར་ཁེ", "མེར་ཀེ")
    s = s.replace("ལོ་ཆིག", "ལོ་གཅིག")
    s = s.replace("ཆེད་པོ", "ཆེན་པོ")
    s = s.replace("ཅེད་པོ", "ཆེན་པོ")
    s = s.replace("ཅེན་པོ", "ཆེན་པོ")
    return s

def test_normalize_old_tib(s):
    assert(normalize_old_tib("དྲངསྟེ") == "དྲངས་ཏེ")
    assert(normalize_old_tib("གཅལྟོ") == "ཅལད་ཏོ")
    assert(normalize_old_tib("གགྀ་") == "གག་གྀ་")


def normalize_bo_token(s):
    remove_tsheg(s)
    normalize_lenient(s)

def normalize_lenient(s):
    # remove some marks
    s = re.sub(r"[\u0f35\u0f37\u0f39]", "", s)
    # retroflex -> dental
    s = s.replace("ཊ", "ཏ")
    s = s.replace("ཋ", "ཐ")
    s = s.replace("ཌ", "ད")
    s = s.replace("ཎ", "ན")
    s = s.replace("ྚ", "ྟ")
    s = s.replace("ྛ", "ྠ")
    s = s.replace("ྜ", "ྡ")
    s = s.replace("ྞ", "ྣ")
    s = s.replace("ཥ", "ཤ")
    s = s.replace("ྵ" , "ྴ") # requires NFD
    # normalize non-semantic graphical variation
    s = s.replace("ྻ", "ྱ")
    s = s.replace("ྼ", "ྲ")
    s = s.replace("ཪ", "ར")
    # a common Sanskrit normalization is r+repeated consonnant
    s = re.sub(r"ར([\u0f90-\u0fbc])\1", r"ར\1", s)
    # anusvara / anunasika normalization
    s = s.replace("\u0f82", "\u0f7e")
    s = s.replace("\u0f83", "\u0f7e")
    s = s.replace("\u0f86", "\u0f7e")
    # normalize gigus
    s = s.replace("\u0f80", "\u0f72") # requires NFD
    # remove achung and wasur
    s = s.replace("ཱ", "")
    s = s.replace("ྺ", "")
    s = s.replace("ྭ", "")
    return s

SUBST_SYLS = None

def get_substs():
    global SUBST_SYLS
    if SUBST_SYLS is not None:
        return SUBST_SYLS
    SUBST_SYLS = {}
    with open(config.BO_SYLLIST_PATH, encoding='UTF-8') as f:
        for l in f.readlines():
            l = l[:-1]
            parts = l.split(",")
            if len(parts) < 2:
                continue
            SUBST_SYLS[parts[0]] = parts[1]
    return SUBST_SYLS

def normalize_substs(s):
    substs = get_substs()
    if s in substs:
        return substs[s]
    return s

def remove_punctuation(s):
    # we assume that Unicode normalization already took place
    s = re.sub(r"[\s\u0f0b\u0fd2]", "", s)
    return s

def normalize_ngatadara(s):
    """
    The Tibetan letters ང, ཏ, ད and ར are often difficult to differentiate
    visually in block prints or poor quality manuscripts, and are often
    confused in manual inputs or OCRs. This function detects some common cases
    of confusion and fixes them. Note that this function assumes that the text
    is Classical Tibetan or the commonly found Sanskrit words, it may very well
    not work for uncommon Sanskrit words.
    """
    s = re.sub(r"(?:དྙ|ངྙ|ཏྙ)", r"རྙ", s)
    s = re.sub(r"^བལྔ", "བལྡ", s)
    s = re.sub(r"(?:ངྲ|རྲ)", "དྲ", s)
    s = re.sub(r"^འ[རངཏ]([\u0f40-\u0fbc])", r"འད\1", s)
    # case where prefix da is read as ra, nga or ta, with a special case for second suffix sa
    s = re.sub(r"^[རངཏ]([བམཀགཔང])([\u0f40-\u0f65\u0f67-\u0fbc])", r"ད\1\2", s)
    s = re.sub(r"(?:དླ|ཏླ|ངླ)", r"རླ", s)
    # TODO: common mistakes in Sanskrit stacks
    # d+n, ng+n -> t+n
    # ng+ng | d+ng | ng+d -> d+d
    return s

NEEDS_A = {
    "ག": {"ཅ": True, "ཉ": True, "ཏ": True, "ད": True, "ན": True, "ཙ": True, "ཞ": True, "ཟ": True, "ཡ": True, "ཤ": True, "ས": True},
    "ད": {"ཀ": True, "ག": True, "ང": True, "པ": True, "བ": True, "མ": True},
    "བ": {"ཀ": True, "ག": True, "ཅ": True, "ཏ": True, "ད": True, "ཙ": True, "ཞ": True, "ཟ": True, "ཤ": True, "ས": True},
    "མ": {"ཁ": True, "ག": True, "ང": True, "ཆ": True, "ཇ": True, "ཉ": True, "ཐ": True, "ད": True, "ན": True, "ཚ": True, "ཛ": True},
    "འ": {"ཁ": True, "ག": True, "ཆ": True, "ཇ": True, "ཐ": True, "ད": True, "ཕ": True, "བ": True, "ཚ": True, "ཛ": True}
}

def remove_affixes(s):
    # usual suffixes
    lens = len(s)
    s = re.sub(r"([\u0f40-\u0fbc])(?:འིའོ|འིའམ|འིའང|འོའམ|འོའང|འིས|འི|འོ|འམ|འང|འས|འད|འར)$", r"\1", s)
    if len(s) != lens and len(s) > 1:
        # if a substitution has been made, make sure to add a suffix འ in the relevant cases:
        if s[-2] in NEEDS_A and s[-1] in NEEDS_A[s[-2]]:
            s += "འ"
    # remove འ suffix when not warranted
    if len(s) > 2 and s[-1] == 'འ' and (s[-3] not in NEEDS_A or s[-2] not in NEEDS_A[s[-3]]):
        s = s[:-1]
    s = s.replace("འུར", "འུ")
    s = s.replace("འུས", "འུ")
    # da drag
    s = re.sub(r"([^གམ][ནལར])ད$", r"\1", s)
    return s


def is_vowel(char):
    if re.search(r'[\u0f71-\u0f84]', char):
        return True
    return False

def is_suffix(char):
    if re.search(r'[\u0f90-\u0fbc]', char):
        return True
    return False


def normalize_invalid_start_tokens(token):
    if is_vowel(token[0]):
        return token[1:]
    if is_suffix(token[0]):
        return token[1:]
    return token

HAS_TIBETAN_RE = re.compile(r"[\u0f00-\u0fd8]")

class TibetanNormalizer(Normalizer):

    def __init__(self, keep_eol = True, normalize_old_tib = False, normalize_semantic = True):
        self.keep_eol = keep_eol
        self.normalize_old_tib = normalize_old_tib
        self.normalize_semantic = normalize_semantic

    def normalize_always(self, s):
        if HAS_TIBETAN_RE.search(s):
            s,_ = normalize_unicode(s)
            s = normalize_graphical(s)
        else:
            s = normalize_punctuation_token_always(s, self.keep_eol)
        return s

    def normalize_pre_token_diff(self, s):
        if HAS_TIBETAN_RE.search(s):
            s = remove_punctuation(s)
            if self.normalize_old_tib:
                s = normalize_old_tib(s)
            s = normalize_lenient(s)
            if self.normalize_semantic:
                s = remove_affixes(s)
                s = normalize_substs(s)
        else:
            s = normalize_punctuation_token_pre_token_diff(s, self.keep_eol)
        return s

    def normalize_pre_token_comparison(self, s):
        s = remove_punctuation(s)
        return s

    def append_normalized_token_string(self, s, token_string):
        return s+token_string

