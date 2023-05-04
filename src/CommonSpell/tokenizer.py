from typing import Tuple, List

from CommonSpell.normalizer import Normalizer
from CommonSpell.encoder import Encoder

Token = Tuple[int, int, int, str]
TokenList = List[Token]

class Tokenizer():
    """
    Tokenizer class used in Vulgalizer.
    """

    def __init__(self, encoder: Encoder, normalizer: Normalizer, stop_words: List[str] = []):
        self.encoder = encoder
        self.normalizer = normalizer
        self.stop_words = stop_words

    def reset(self):
        self.encoder.reset()

    def tokenize(self, s: str, start: int = 0, end: int = None) -> Tuple[str, TokenList]:
        """
        A function that takes as arguments:
        - a string to tokenize
        - a encoder
        - start: an optional character position at which the tokenization
                 must start in the string
        - end: an optional character position at which the tokenization must end
        
        It returns two results:
        - token_string: a string representing the tokens encoded in the encoder
        - a list of tokens, where a token is a tuple of three numbers:
          * the character position of the start of token in s
          * the character position of the end of the token in s
          * position_increment: the number of characters in the token string that correspond to the token

        The position_increment number is inspired from the PositionIncrementAttribute from Apache Lucene.
        It is 1 in the general case, but is 0 for a token we want to ignore in a diff (stop word, some punctuation, etc.).
        It can also be greater than 1 in the case of shorthands. For instance the function could
        tokenize the token "I'm" as two characters (corresponding to "I" and "am" in the encoder)
        in the token_string, in which case the position_increment is 2.

        A default implementation is not provided.
        """
        return "", []


