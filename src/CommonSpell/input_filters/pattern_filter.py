import re
from typing import Pattern
from CommonSpell.input_filters.input_filter import InputFilter
import logging

class PatternInputFilter(InputFilter):

    """
    Regex Filter inspired from Apache Lucene's PatternReplaceCharFilter
    """

    REPL_STR_SIMPLE = 0
    REPL_STR_COMPLEX = 1
    REPL_FUN = 2

    def __init__(self, arg, pattern: Pattern, replacement):
        super().__init__(arg)
        self.pattern = pattern
        self.replacement = replacement
        self.replacement_type = self.REPL_STR_SIMPLE
        if callable(replacement):
            self.replacement_type = self.REPL_FUN
        elif "\\" in replacement:
            self.replacement_type = self.REPL_STR_COMPLEX
            logging.warn("please use function instead of substitution strings in PatternInputFilter")
        self.replacement_len = 0 if self.replacement_type != self.REPL_STR_SIMPLE else len(replacement)

    def get_string(self):
        orig = self.get_arg_string()
        last_match_end = 0
        output = ""
        output_len = 0
        cumulative = 0
        for m in self.pattern.finditer(orig):
            group_size = m.end() - m.start()
            skipped_size = m.start() - last_match_end
            output += orig[last_match_end:m.start()]
            last_match_end = m.end()
            output_len += skipped_size

            replacement = ""
            replacement_len = 0

            if self.replacement_type == self.REPL_FUN:
                # if replacement is a function we can just apply it on the match
                replacement = self.replacement(m)
                replacement_len = len(replacement)
            elif self.replacement_type == self.REPL_STR_SIMPLE:
                # if the replacement is a simple string with no substitution,
                # we can use it directly
                replacement = self.replacement
                replacement_len = self.replacement_len
            elif self.replacement_type == self.REPL_STR_COMPLEX:
                # If the replacement has some substitutions:
                # Unfortunately the Python re match object does not allow
                # substitution (as far as I can see), so we have to apply
                # the regexp again on the match. This module will thus
                # not have the same high performance as an implementation
                # in a different language. There might be better ways to 
                # do this, suggestions welcome!
                replacement = self.pattern.sub(self.replacement, m.group(0), count=1)
                replacement_len = len(replacement)
            
            if replacement_len < group_size:
                cumulative += group_size - replacement_len
                position = output_len + replacement_len
                self.add_position_diff(position, cumulative)
            elif replacement_len > group_size:
                # when the replacement is large, new indexes point to
                # the last original index
                for i in range(group_size, replacement_len):
                    cumulative -= 1
                    self.add_position_diff(output_len+i, cumulative)

            output += replacement
            output_len += replacement_len

        if last_match_end == 0:
            # no match (?)
            return orig

        if last_match_end < len(orig):
            output += orig[last_match_end:]

        return output

