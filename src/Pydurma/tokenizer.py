from typing import Tuple, List

from Pydurma.normalizer import Normalizer
from Pydurma.encoder import Encoder
from Pydurma.input_filters.input_filter import InputFilter

Token = Tuple[int, int, int, str, int]
TokenList = List[Token]

class Tokenizer():
    """
    Tokenizer class used in Vulgalizer.
    """

    def __init__(self, encoder: Encoder, normalizer: Normalizer):
        self.encoder = encoder
        self.normalizer = normalizer

    def reset(self):
        self.encoder.reset()
    
    def get_input(self, arg):
        """
        returns the input data from the argument, which can be a string or an InputFilter

        returns:
           - the string to be tokenized
           - the function to correct the positions to get those of the original string
        """
        if isinstance(arg, InputFilter):
            return arg.get_string(), arg.correct_position
        return arg, lambda x: x

    def tokenize(self, arg) -> Tuple[str, TokenList]:
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


