import logging
from typing import List, Dict

from Pydurma.tokenizer import Token, TokenList
from Pydurma.encoder import Encoder
from Pydurma.aligners.aligner import TokenMatrix


def token_row_to_text_row(
    token_row: List[Token], basestr: str, text_for_gap: str = "-"
):
    text_row = []
    for t in token_row:
        if t is None:
            text_row.append(text_for_gap)
        else:
            text_row.append(basestr[t[0] : t[1]])
    return text_row


def token_row_to_token_str_rows(token_row: List[Token], text_for_gap: str = "-"):
    text_row = []
    for t in token_row:
        if t is None:
            text_row.append(text_for_gap)
        else:
            text_row.append(t[3])
    return text_row


def column_matrix_to_row_matrix(column_matrix):
    nb_columns_transformed = len(column_matrix)
    nb_rows_transformed = len(column_matrix[0])
    row_matrix = [
        [None for _ in range(nb_columns_transformed)]
        for _ in range(nb_rows_transformed)
    ]
    for i, column_transformed in enumerate(column_matrix):
        for j, cell in enumerate(column_transformed):
            row_matrix[j][i] = cell
    return row_matrix


def token_row_to_string(token_row: List[Token], basestr: str):
    string_row = []
    for t in token_row:
        if t is None:
            string_row.append()
        string_row.append()


def get_debug_token_matrix_str(
    token_matrix: TokenMatrix,
    text_for_gap: str = "-",
    original_strings: List[str] = None,
):
    # print the table horizontally
    from prettytable import PrettyTable

    x = PrettyTable()
    x.header = False
    horizontal_matrix = column_matrix_to_row_matrix(token_matrix)
    for row_i, token_row in enumerate(horizontal_matrix):
        string_row = None
        if original_strings:
            string_row = token_row_to_text_row(
                token_row, original_strings[row_i], text_for_gap
            )
        else:
            string_row = token_row_to_token_str_rows(token_row, text_for_gap)
        x.add_row(string_row)
    x.align = "l"
    return x.get_string()


def debug_token_matrix(
    logger, token_matrix, text_for_gap="-", original_strings: List[str] = None
):
    if not logger.isEnabledFor(logging.DEBUG):
        return
    debug_str = get_debug_token_matrix_str(token_matrix, text_for_gap, original_strings)
    logger.debug("\n" + debug_str)


def debug_token_lists(logger, token_lists, string_list=None):
    if not logger.isEnabledFor(logging.DEBUG):
        return
    for i, token_list in enumerate(token_lists):
        row_string = ""
        for t in token_list:
            if t is None:
                row_string += " - "
            elif string_list:
                token_in_string = string_list[i][t[0] : t[1]]
                row_string += " '%s'[%d:%d:%d;%s] " % (
                    token_in_string,
                    t[0],
                    t[1],
                    t[2],
                    t[3],
                )
            else:
                row_string += " '%s'[%d:%d:%d] " % (t[3], t[0], t[1], t[2])
        logger.debug(row_string)


def debug_token_strings(logger, token_strings: List[str], encoder: Encoder):
    if not logger.isEnabledFor(logging.DEBUG):
        return
    for token_string in token_strings:
        print(encoder.decode_string(token_string))

def get_token_strings(tokens: TokenList, version_paths) -> Dict:
    token_strings = {}
    for version_index, token in enumerate(tokens):
        version_name = version_paths[version_index].stem
        try:
            token_strings[version_name] = token[3]
        except:
            token_strings[version_name] = ''
    return token_strings

def is_diff_token(tokens: TokenList) -> bool:
    token_strings = [token[3] if token is not None and token[3] is not None else '' for token in tokens]
    if len(list(set(token_strings))) == 1:
        return False
    return True


def get_top_weight_index(tokens):
        top_weight = 0
        top_token_index = 0
        for j, token in enumerate(tokens):
            if token is not None and token[4] > top_weight:
                top_weight = token[4]
                top_token_index = j
        return top_token_index
