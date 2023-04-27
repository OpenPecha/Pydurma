import json
import logging

from pathlib import Path

from openpecha.core.ids import get_base_id, get_uuid
from openpecha.core.pecha import OpenPecha
from CommonSpell.bo.normalizer_bo import TibetanNormalizer
from CommonSpell.bo.tokenizer_bo import TibetanTokenizer
from CommonSpell.utils.opf_utils import OPCursor
from CommonSpell.utils.utils import (
    debug_token_lists,
    debug_token_matrix,
    debug_token_strings,
)
from CommonSpell.vocabulary import Vocabulary
from CommonSpell.vulgaligners.vulgaligner_fdmp import FDMPVulgaligner
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher
from CommonSpell.weighers.token_weigher_count import TokenCountWeigher
from CommonSpell.weighers.token_weigher_valid_bo import ValidBoTokenWeigher

logger = logging.getLogger("PlainTextCommonSpeller")

class PlainTextCommonSpeller():

    def __init__(self, op_output: OpenPecha) -> None:
        self.vocabulary = Vocabulary()
        self.aligner = FDMPVulgaligner()
        self.normalizer = TibetanNormalizer()
        # stop words only make sense when comparing different editions, not ocr of the
        # same scans
        self.tokenizer = TibetanTokenizer(self.vocabulary, self.normalizer, stop_words=[])
        self.text_paths = []
        self.op_output = op_output
    
    def get_matrix_weigher(self):
        matrix_weigher = TokenMatrixWeigher()
        matrix_weigher.add_weigher(TokenCountWeigher(), 1)
        matrix_weigher.add_weigher(ValidBoTokenWeigher(weight_gap=100, relative=True), 1)
        return matrix_weigher

    def add_witness(self, text_path: Path):
        self.text_paths.append(text_path)
    
    def get_vulga_report(self, tokens, weights, top_weight_index):
        vulga_report = {}
        token_id = get_uuid()
        vulga_report[token_id] = {}
        for token_index, (token, weight) in enumerate(zip(tokens, weights)):
            if token is None:
                token_string = ""
            else:
                token_string = token[3]
            if token_index == top_weight_index:
                vulga_report[token_id][f'W{token_index}'] = {
                    'text': token_string,
                    'weight': weight,
                    'is_top_weight': True
                }
            else:
                vulga_report[token_id][f'W{token_index}'] = {
                    'text': token_string,
                    'weight': weight,
                    'is_top_weight': False
                }
        return vulga_report

    def append_segments(self, segments, op_cursor):
        token_strings = []
        token_lists = []
        cur_page_vulga_report = {}
        for segment in segments:
            token_list, token_string = self.tokenizer.tokenize(segment)
            token_strings.append(token_string)
            token_lists.append(token_list)
        token_matrix = self.aligner.get_alignment_matrix(token_strings, token_lists)
        # uncomment to debug the main variables:
        debug_token_lists(logger, token_lists)
        debug_token_strings(logger, token_strings, self.vocabulary)
        debug_token_matrix(logger, token_matrix)
        matrix_weigher = self.get_matrix_weigher()
        weight_matrix = matrix_weigher.get_weight_matrix(token_matrix)
        for row_i, tokens in enumerate(token_matrix):
            # for each set of aligned tokens, take the string of the token
            # with the biggest weight
            top_weight = 0
            top_token_index = 0
            weights = weight_matrix[row_i]
            for j, weight in enumerate(weights):
                if weight is not None and weight > top_weight:
                    top_weight = weight
                    top_token_index = j
            cur_page_vulga_report.update(self.get_vulga_report(tokens, weights, top_token_index))
            token = tokens[top_token_index]
            if top_token_index != 0 and logger.isEnabledFor(logging.DEBUG):
                logger.debug("election: %s -> %s", str(tokens), token)
            if token is None:
                # gap is the most likely value, we just skip
                continue
            op_cursor.append_token(token)
        return cur_page_vulga_report
    
    def save_vulga_report(self, vulga_report_path, base_vulga_report, base_id):
        base_vulga_report_json = json.dumps(base_vulga_report, ensure_ascii=False)

        (vulga_report_path / f"{base_id}.json").write_text(base_vulga_report_json, encoding="utf-8")
        

    # @timed(unit='s', name="Compute vulgate text(plain text): ")
    def create_vulgate(self):
        if len(self.text_paths) < 2:
            logging.error("cannot create vulgate with just 1 edition")
            return
        base_id = get_base_id()
        (self.op_output.opf_path / "vulga_report").mkdir(parents=True, exist_ok=True)
        vulga_report_path = self.op_output.opf_path / "vulga_report"
        
        cur_base_vulga_report = {}
        cursor = OPCursor(self.op_output, base_id, 0)
        segments = []
        for text_path in self.text_paths:
            text = text_path.read_text(encoding='utf-8')
            segments.append(text)
            
        try:
            cur_base_vulga_report.update(self.append_segments(segments, cursor))
        except KeyboardInterrupt as e:
            raise e
        except:
            logging.exception("exception in text %s", text_path.stem)
        cursor.flush()
        self.op_output.save_base()
        self.op_output.save_layers()
        cur_base_vulga_report['witness_mapping'] = {}
        self.save_vulga_report(vulga_report_path, cur_base_vulga_report, base_id)
            

