import re
from typing import List

from Pydurma.tokenizer import Token
from Pydurma.weighers.token_weigher import TokenWeigher

# well formed Classical Tibetan according to
# https://doi.org/10.5070/H917135529
# conventions used in https://github.com/eroux/hunspell-bo

# affixes that can go after syllables that can't take any usual suffix, like དྲིའུ
VAL_BO_C_BASE = "འི|འོ|འིའོ|ར|ས|འང|འམ|འིའང|འིའམ|འོའང|འོའམ"
VAL_BO_C = "(?:" + VAL_BO_C_BASE + ")"
# the usual suffixes (except འ) + affixes
VAL_BO_S = "ག|གས|ང|ངས|ད|ན|བ|བས|མ|མས|ལ|" + VAL_BO_C_BASE
# vowel + usual suffixes and affixes, the most common case, can go at the
# end of the usual syllables like རྐ
VAL_BO_A = "[\u0f72\u0f74\u0f7a\u0f7c]?(?:" + VAL_BO_S + ")?"
# end of syllables that can take a འ but that could be invalid without it, like དཀ
VAL_BO_NB = "(?:འ|[\u0f72\u0f74\u0f7a\u0f7c](?:" + VAL_BO_S + ")?|(?:" + VAL_BO_S + "))"
# the most common case
VAL_BO_WITH_A = "(?:ཧྥ|ཀ|ཀྱ|ཀྲ|ཀླ|དཀྱ|དཀྲ|བཀྱ|བཀྲ|བཀླ|རྐ|རྐྱ|ལྐ|སྐ|སྐྱ|སྐྲ|བརྐ|བརྐྱ|བསྐ|བསྐྱ|བསྐྲ|ཁ|ཁྱ|ཁྲ|མཁྱ|མཁྲ|འཁྱ|འཁྲ|ག|གྱ|གྲ|གླ|དགྱ|དགྲ|བགྱ|བགྲ|མགྱ|མགྲ|འགྱ|འགྲ|རྒ|རྒྱ|ལྒ|སྒ|སྒྱ|སྒྲ|བརྒ|བརྒྱ|བསྒ|བསྒྱ|བསྒྲ|ང|རྔ|ལྔ|སྔ|བརྔ|བསྔ|ཅ|ལྕ|ཆ|ཇ|རྗ|ལྗ|བརྗ|ཉ|རྙ|སྙ|བརྙ|བསྙ|ཏ|རྟ|ལྟ|སྟ|བརྟ|བལྟ|བསྟ|ཐ|ད|དྲ|འདྲ|རྡ|ལྡ|སྡ|བརྡ|བལྡ|བསྡ|ན|རྣ|སྣ|བརྣ|བསྣ|པ|པྱ|པྲ|དཔྱ|དཔྲ|ལྤ|སྤ|སྤྱ|སྤྲ|ཕ|ཕྱ|ཕྲ|འཕྱ|འཕྲ|བ|བྱ|བྲ|བླ|དབྱ|དབྲ|འབྱ|འབྲ|རྦ|ལྦ|སྦ|སྦྱ|སྦྲ|མ|མྱ|དམྱ|རྨ|རྨྱ|སྨ|སྨྱ|ཙ|རྩ|སྩ|བརྩ|བསྩ|ཚ|ཛ|རྫ|བརྫ|ཝ|ཞ|ཟ|ཟླ|བཟླ|འ|ཡ|ར|རླ|བརླ|ལ|ཤ|ས|སྲ|སླ|བསྲ|བསླ|ཧ|ཧྲ|ལྷ|ཨ)"
# syllables that can't take an unsual suffix but can take an affix
VAL_BO_WITH_C = "(?:བགླ|ཏྲ|མྲ|སྨྲ|སྨྲེ|རྒྭ|ཀརྨ|པདྨ|ཨཱ|རྒྭ|བསྭེ|རྭི|དྭ|ཀྲའུ|ཀྲུའུ|ཁྲུའུ|སྒྱིའུ|ཅོའུ|གཅོའུ|ཐུའུ|དུའུ|དྲིའུ|ཕེའུ|མུའུ|མོའུ|ཚུའུ|ལོའུ|ཧུའུ|ཧེའུ|ཧྲུའུ|བྲའོ|སླེའོ|ཀའུ|ཀིའུ|ཀེའུ|ཁིའུ|ཁེའུ|ཁྱིའུ|ཁྱེའུ|ཁྲིའུ|ཁྲེའུ|གའུ|གྲིའུ|གྲེའུ|གླེའུ|འགིའུ|རྒེའུ|སྒའུ|སྒེའུ|སྒྱེའུ|སྒྲེའུ|རྔེའུ|སྔེའུ|ཅེའུ|གཅིའུ|གཅེའུ|ལྕེའུ|རྗེའུ|ཉེའུ|སྙེའུ|ཏེའུ|གཏེའུ|རྟའུ|རྟེའུ|སྟེའུ|ཐའུ|ཐིའུ|ཐེའུ|ཐོའུ|མཐེའུ|དེའུ|དྲེའུ|མདེའུ|རྡེའུ|ལྡེའུ|སྡེའུ|ནའུ|ནེའུ|སྣེའུ|དཔེའུ|སྤའུ|སྤེའུ|སྤྱིའུ|སྤྲེའུ|ཕྲའུ|ཕྲེའུ|འཕེའུ|བེའུ|བྱའུ|བྱིའུ|བྱེའུ|བྲའུ|བྲེའུ|བྲོའུ|འབེའུ|སྦྲེའུ|མིའུ|མྱིའུ|རྨེའུ|སྨེའུ|ཙིའུ|ཙེའུ|གཙེའུ|རྩིའུ|རྩེའུ|ཚའུ|ཚེའུ|མཚེའུ|མཚེའུ|རྫིའུ|རྫེའུ|གཞུའུ|ཟེའུ|ཡེའུ|གཡིའུ|རེའུ|ལའུ|ལིའུ|ལེའུ|ཤའུ|ཤེའུ|སིའུ|སེའུ|སྲིའུ|སླེའུ|བསེའུ|ཨའུ|ཀྭ|ཀྭའི|ཁྭ|གྭ|གྲྭ|ཉྭ|དྭོ|དྲྭ|ཕྱྭ|རྩྭ|ཚྭ|ཞྭ|ཟྭ|རྭ|ལྭ|ཤྭ|སྭོ|བསྭ|བསྭོ|ཧྭ)"
# syllables that can take a འ
VAL_BO_WITH_NB = "(?:དཀ|བཀ|མཁ|འཁ|དག|བག|མག|འག|དང|མང|གཅ|བཅ|མཆ|འཆ|མཇ|འཇ|གཉ|མཉ|གཏ|བཏ|མཐ|འཐ|གད|བད|མད|འད|གན|མན|དཔ|འཕ|དབ|འབ|དམ|གཙ|བཙ|མཚ|འཚ|མཛ|འཛ|གཞ|བཞ|གཟ|བཟ|གཡ|གཤ|བཤ|གས|བས)"
# syllables that can't take a suffix or affix
VAL_BO_STDA = "(?:དམེའ|མེའ|མདྲོན|བརྡའ|བརྟའ|ཏྲེས|ཐྲིག|སྨྲོས|སྨྲས|སྨྲེང|སྨྲངས|སྨྲང|སྣྲོན|སྣྲུབས|སྣྲེལ|རྭང|དྭང|ཏྭོན|ཀྭན|ཀྭས|ཧྭང|དབའས|ནོའུར|དྭངས|དྭགས|ཚྭབ|ཧྭག|ཧྭགས)"

VAL_BO_PAT_STR = (
    "(?:"
    + VAL_BO_STDA
    + "|"
    + VAL_BO_WITH_NB
    + VAL_BO_NB
    + "|"
    + VAL_BO_WITH_C
    + VAL_BO_C
    + "|"
    + VAL_BO_WITH_A
    + VAL_BO_A
    + ")[\u0f0c\u0f0b\u0fd2\\s]?"
)

# print(VAL_BO_PAT_STR)

VAL_BO_RE = re.compile(VAL_BO_PAT_STR)
HAS_TIB_LETTERS = re.compile(r"[\u0f40-\u0f6c]")


class ValidBoTokenWeigher(TokenWeigher):
    """
    Returns a weigh of:
    - 1 if the token is a valid Tibetan syllable (followed by an optional tsheg)
    - 0 if the token is an invalid Tibetan syllable
    - 1 if the token is not a Tibetan syllable at all or a gap
    """

    def __init__(
        self,
        weight_invalid=70,
        weight_nontibetan: int = None,
        weight_gap: int = None,
        relative=True,
    ):
        super().__init__(relative)
        self.weight_invalid = weight_invalid
        self.weight_nontibetan = weight_nontibetan
        self.weight_gap = weight_gap

    def weigh(self, column: List[Token]) -> List[int]:
        weights = []
        for t in column:
            if t is None:
                weights.append(self.weight_gap)
                continue
            s = t[3]
            if not HAS_TIB_LETTERS.search(s):
                # logging.debug("%s is not Tibetan", s)
                weights.append(self.weight_nontibetan)
            elif VAL_BO_RE.fullmatch(re.sub(r"[\s\u0f0b\u0fd2]", "", s)) is not None:
                # ignore following punctuation
                # logging.debug("%s is valid Tibetan", s)
                weights.append(100)
            else:
                # logging.debug("%s is invalid Tibetan", s)
                weights.append(self.weight_invalid)
        return weights
