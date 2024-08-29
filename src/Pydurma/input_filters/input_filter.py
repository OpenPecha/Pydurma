import re
from bisect import bisect, bisect_left
from typing import List, Tuple

class InputFilter():

    """
    Inspired from Apache Lucene's BaseCharFilter. An input filter
    does not filter input, but represents a filtered input. The name
    "filter" is kept mostly for keeping the parallel with Lucene.

    For optimization purposes, the get_string() function of filters 
    can only be called once and the filters do not store their input
    or output string (so that only one string is stored
    in memory when filters are chained).

    The typical code for input filtering is slightly unintuitive and goes like:

    inpt = "my string"
    inpt = Filter1(inpt, filter1_params)
    inpt = Filter2(inpt, filter2_params)
    tokenstr, tokens = Tokenizer.tokenize(inpt)
    """

    def __init__(self, arg):
        # can be initalized with a string or another InputFilter
        self.positions = []
        self.diffs = []
        self.arg = arg
        if isinstance(arg, str):
            self.string = arg
            self.previous_filter = None
        if isinstance(arg, InputFilter):
            self.string = None
            self.previous_filter = arg
        # we can only call the input filters once for performance sake
        self.done = False

    def correct(self, current_position):
        """
        corrects a position in this filter only
        """
        previous_position_i = bisect(self.positions, current_position)
        if previous_position_i is None or previous_position_i < 1:
            return current_position
        return current_position + self.diffs[previous_position_i-1]

    def correct_position(self, current_position):
        """
        corrects the position recursively
        """
        corrected = self.correct(current_position)
        if self.previous_filter is None:
            return corrected
        return self.previous_filter.correct_position(corrected)

    def add_position_diff(self, position: int, cumulative_diff: int):
        """
        the main function to use in subclasses, indicate position diffs
        in the current string
        """
        # we cannot go back with a filter
        assert(not self.positions or position >= self.positions[-1])
        if not self.positions or position > self.positions[-1]:
            self.positions.append(position)
            self.diffs.append(cumulative_diff)
        else:
            # case where we overwrite the latest diff
            self.diffs[-1] = cumulative_diff

    def get_arg_string(self) -> str:
        # can only be called once
        assert(self.done == False)
        self.done = True
        if self.string is not None:
            return self.string
        return self.previous_filter.get_string()

    def get_string(self):
        """
        The main function to be implemented by subclasses
        """
        return self.get_arg_string()
