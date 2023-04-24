import json
import logging

from openpecha.core.ids import get_uuid
from openpecha.core.layer import LayerEnum
from openpecha.core.pecha import OpenPecha

from vulgatizer.bo.normalizer_bo import TibetanNormalizer
from vulgatizer.bo.tokenizer_bo import TibetanTokenizer
from vulgatizer.utils.opf_utils import (
    OPCursor,
    OPFragmentLayerAccessor,
    OPSegment,
    find_annotation_of_reference,
    find_comparable_base_id,
)
from vulgatizer.utils.utils import (
    debug_token_lists,
    debug_token_matrix,
    debug_token_strings,
)
from vulgatizer.vocabulary import Vocabulary
from vulgatizer.vulgaligners.vulgaligner_fdmp import FDMPVulgaligner
from vulgatizer.weighers.matrix_weigher import TokenMatrixWeigher
from vulgatizer.weighers.token_weigher_count import TokenCountWeigher
from vulgatizer.weighers.token_weigher_op_confidence import OPConfidenceTokenWeigher
from vulgatizer.weighers.token_weigher_valid_bo import ValidBoTokenWeigher

logger = logging.getLogger("VulgatizerOPTibOCR")


class VulgatizerOPTibOCR():

    def __init__(self, op_output: OpenPecha):
        # no need for the vocabulary to decode if we're not debugging
        self.vocabulary = Vocabulary(allow_decode=logger.isEnabledFor(logging.DEBUG))
        self.aligner = FDMPVulgaligner()
        self.normalizer = TibetanNormalizer()
        # stop words only make sense when comparing different editions, not ocr of the
        # same scans
        self.tokenizer = TibetanTokenizer(self.vocabulary, self.normalizer, stop_words=[])
        self.ops = []
        self.op_output = op_output

    def get_matrix_weigher(self, confidence_layer_accessors):
        matrix_weigher = TokenMatrixWeigher()
        matrix_weigher.add_weigher(TokenCountWeigher(), 1)
        matrix_weigher.add_weigher(ValidBoTokenWeigher(weight_gap=100, relative=True), 1)
        matrix_weigher.add_weigher(OPConfidenceTokenWeigher(confidence_layer_accessors, relative=False), 1)
        return matrix_weigher

    def add_op_witness(self, op: OpenPecha):
        self.ops.append(op)
    
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

    def append_segments(self, op_segments, op_cursor):
        token_strings = []
        token_lists = []
        confidence_layer_accessors = []
        cur_page_vulga_report = {}
        for segment in op_segments:
            token_list, token_string = segment.tokenize(self.tokenizer)
            token_strings.append(token_string)
            token_lists.append(token_list)
            confidence_layer_accessors.append(OPFragmentLayerAccessor(segment, LayerEnum.ocr_confidence))
        token_matrix = self.aligner.get_alignment_matrix(token_strings, token_lists)
        # uncomment to debug the main variables:
        debug_token_lists(logger, token_lists)
        debug_token_strings(logger, token_strings, self.vocabulary)
        debug_token_matrix(logger, token_matrix)
        matrix_weigher = self.get_matrix_weigher(confidence_layer_accessors)
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
            ocr_confidence = OPConfidenceTokenWeigher.get_lowest_confidence(confidence_layer_accessors[top_token_index], token[0], token[1])
            op_cursor.append_token(token, ocr_confidence)
        return cur_page_vulga_report
    
    def save_vulga_report(self, vulga_report_path, base_vulga_report, base_id):
        base_vulga_report_json = json.dumps(base_vulga_report, ensure_ascii=False)

        (vulga_report_path / f"{base_id}.json").write_text(base_vulga_report_json, encoding="utf-8")
        

    # @timed(unit='s', name="Compute vulgate text(op): ")
    def create_vulgate(self):
        if len(self.ops) < 2:
            logging.error("cannot create vulgate with just 1 edition")
            return
        base_op = self.ops[0]
        other_ops = self.ops[1:]
        (self.op_output.opf_path / "vulga_report").mkdir(parents=True, exist_ok=True)
        vulga_report_path = self.op_output.opf_path / "vulga_report"
        for base_id, base_info in base_op.meta.bases.items():
            base_pagination = base_op.get_layer(base_id, LayerEnum.pagination)
            other_paginations = {}
            other_base_ids = {}
            cur_base_vulga_report = {}
            cursor = OPCursor(self.op_output, base_id, 0)
            for other_op in other_ops:
                other_base_id = find_comparable_base_id(base_op, base_id, other_op)
                other_base_ids[other_op.pecha_id] = other_base_id
                other_pagination = other_op.get_layer(other_base_id, LayerEnum.pagination)
                other_paginations[other_op.pecha_id] = other_pagination
            for ann in base_pagination.annotations.values():
                img_id = ann["reference"]
                segments = []
                segments.append(OPSegment(base_op, base_id, ann["span"]["start"], ann["span"]["end"]))
                for other_op in other_ops:
                    other_pagination = other_paginations[other_op.pecha_id]
                    if other_pagination is None:
                        continue
                    other_base_id = other_base_ids[other_op.pecha_id]
                    if other_base_id is None:
                        continue
                    other_ann = find_annotation_of_reference(other_pagination, ann["reference"])
                    if other_ann is None:
                        continue
                    segments.append(OPSegment(other_op, other_base_id, other_ann["span"]["start"], other_ann["span"]["end"]))
                try:
                    cur_base_vulga_report.update(self.append_segments(segments, cursor))
                except KeyboardInterrupt as e:
                    raise e
                except:
                    logging.exception("exception in page %s", ann["reference"])
                cursor.end_page(ann)
                self.tokenizer.reset()
            # clear cache at the end of each base
            base_op.reset_base_and_layers()
            for other_op in other_ops:
                other_op.reset_base_and_layers()
            cursor.flush()
            self.op_output.save_base()
            self.op_output.save_layers()
            self.op_output.reset_base_and_layers()
            cur_base_vulga_report['witness_mapping'] = {}
            for op_walker, op in enumerate(self.ops):
                cur_base_vulga_report['witness_mapping'][f'W{op_walker}'] = op.meta.source_metadata.get('pub_name')
            self.save_vulga_report(vulga_report_path, cur_base_vulga_report, base_id)
            

