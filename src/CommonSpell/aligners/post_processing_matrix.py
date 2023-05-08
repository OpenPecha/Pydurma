from CommonSpell.utils.utils import is_diff_token

def is_consecutive_diff_token(prev_tokens_entry, tokens_entry):
     if is_diff_token(prev_tokens_entry) and is_diff_token(tokens_entry):
          return True
     return False

def get_new_token_entry(prev_token, cur_token):
    new_token_entry = ()
    if cur_token:
        merged_token_string = prev_token[3]+cur_token[3]
        new_token_entry = (prev_token[0],cur_token[1], cur_token[2], merged_token_string)
    else:
        new_token_entry = prev_token
    return new_token_entry

def merge_consecutive_diff_tokens_entry(prev_tokens_entry, tokens_entry):
    merged_tokens_entry = []
    for prev_token, cur_token in zip(prev_tokens_entry, tokens_entry):
        new_token_entry = get_new_token_entry(prev_token, cur_token)
        merged_tokens_entry.append(new_token_entry)
    return merged_tokens_entry

def merge_consecutive_diff_tokens_entries(token_matrix):
    postprocessed_matrix = [token_matrix[0]]

    prev_tokens_entry = token_matrix[0]
    entry_walker = 1
    for tokens_entry in token_matrix[1:]:
        if is_consecutive_diff_token(prev_tokens_entry, tokens_entry):
             tokens_entry = merge_consecutive_diff_tokens_entry(prev_tokens_entry, tokens_entry)
             postprocessed_matrix[entry_walker-1] = tokens_entry
        else:
            postprocessed_matrix.append(tokens_entry)
            entry_walker += 1
        prev_tokens_entry = tokens_entry
    return postprocessed_matrix




