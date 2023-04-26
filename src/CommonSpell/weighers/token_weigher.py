from typing import List

from CommonSpell.tokenizer import Token

class TokenWeigher():
    """
    A simple interface to weigh a list of strings with their likelihood
    of being the "correct" one according to a specific criterium.
    """

    def __init__(self, relative=False):
        self.relative = relative

    def weigh(self, column: List[Token]) -> List[int]:
        """
        The main function, takes a column of the alignment matrix and
        returns the associated weights, which should be integers between 0 and 100.

        TODO: while intuitive at first, the idea to always weigh per column is actually
        not very efficient. It could be better to have different types of weighers since
        most work at the token level, not at the column level.
        """
        pass