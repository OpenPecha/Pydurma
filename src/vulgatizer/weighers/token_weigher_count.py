from typing import List

from vulgatizer.weighers.token_weigher import TokenWeigher
from vulgatizer.tokenizers.tokenizer import Token


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
            d[s] = 1 if s not in d else d[s]+1
        total_occurrences = len(column)
        for t in column:
            cur_count = d[t[3] if t is not None else ""]
            weight = int((cur_count / total_occurrences) * 100)
            weights.append(weight)
        return weights

def test_count_weigher():
    cw = CountWeigher()
    assert(cw.weigh(["a", "b", None, "b", "c", None, "a", "b"]) == [25, 37, 25, 37, 12, 25, 25, 37])

if __name__ == "__main__":
    test_count_weigher()