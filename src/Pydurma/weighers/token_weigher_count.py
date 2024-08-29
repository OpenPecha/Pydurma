from typing import List

from Pydurma.tokenizer import Token
from Pydurma.weighers.token_weigher import TokenWeigher


class TokenCountWeigher(TokenWeigher):
    """
    Returns the number of occurences of each token as the weight.
    """

    def weigh(self, column: List[Token]) -> List[int]:
        weights = []
        d = {}
        for t in column:
            s = ""
            if t is not None:
                s = t[3]
            d[s] = 1 if s not in d else d[s] + 1
        total_occurrences = len(column)
        for t in column:
            cur_count = d[t[3] if t is not None else ""]
            weight = int((cur_count / total_occurrences) * 100)
            weights.append(weight)
        return weights
