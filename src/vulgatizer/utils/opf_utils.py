from bisect import bisect
from openpecha.core.pecha import OpenPecha
from openpecha.core.pecha import OpenPechaFS
from openpecha.core.layer import Layer, LayerEnum, PechaMetadata
from openpecha.core.annotations import OCRConfidence, Pagination, Span, BaseAnnotation
from typing import List

from vulgatizer.tokenizer import Token

class OPSegment:
    """
    A segment of an OPF
    """
    def __init__(self, op: OpenPecha, base_id: str, start: int, end: int):
        self.op = op
        self.base_id = base_id
        self.start = start
        self.end = end

    def get_str(self):
        base = self.op.get_base(self.base_id)
        return base[self.start:self.end]

    def tokenize(self, tokenizer):
        base = self.op.get_base(self.base_id)
        return tokenizer.tokenize(base, self.start, self.end)


class OPFragmentLayerAccessor():

    def __init__(self, op_segment: OPSegment, layer_type: LayerEnum, can_overlap=False):
        self.start_chars = []
        self.start_chars_to_ann = {}
        layer: Layer = op_segment.op.get_layer(op_segment.base_id, layer_type)
        if layer is None:
            return
        for annotation_id, annotation in layer.get_annotations():
            if annotation.span is None:
                continue
            # check if annotation is in the interval
            if annotation.span.end >= op_segment.start and annotation.span.start <= op_segment.end:
                self.start_chars_to_ann[annotation.span.start] = annotation
        self.start_chars = sorted(self.start_chars_to_ann.keys())
        # this only works in the case where annotations don't overlap
        # TODO: more general case

    def get_annotations_in_range(self, start: int, end: int) -> List[BaseAnnotation]:
        res = []
        if len(self.start_chars) == 0:
            return res
        start_char_before_i = bisect(self.start_chars, start)
        if start_char_before_i is None:
            return res
        while start_char_before_i < len(self.start_chars):
            start_char = self.start_chars[start_char_before_i]
            if start_char > end:
                return res
            annotation = self.start_chars_to_ann[start_char]
            res.append(annotation)
            start_char_before_i += 1
        return res


class OPCursor:
    """
    A cursor in an opf, has the following components:
    - base layer id
    - start (int)
    """
    def __init__(self, op: OpenPecha, base_id: str, coord: int):
        self.op = op
        self.base_id = base_id
        base = op.get_base(self.base_id)
        if base is None:
            base = ""
        self.base = base
        self.coord = coord
        self.last_page_start = 0

    def append_token(self, token: Token, token_confidence: int):
        if not token or not token[3]:
            return
        self.base += token[3]
        next_coord = self.coord+len(token[3])
        if token_confidence is not None:
            confidence_layer = self.op.get_layer(self.base_id, LayerEnum.ocr_confidence)
            annotation = OCRConfidence(confidence=token_confidence/100, span=Span(start=self.coord, end=next_coord))
            confidence_layer.set_annotation(annotation)
        self.coord = next_coord

    def end_page(self, base_pagination_annotation):
        self.base += "\n\n"
        annotation = Pagination(
            reference=base_pagination_annotation["reference"],
            imgnum=base_pagination_annotation["imgnum"],
            span=Span(start=self.last_page_start, end=self.coord))
        pagination_layer = self.op.get_layer(self.base_id, LayerEnum.pagination)
        pagination_layer.set_annotation(annotation)
        self.coord += 2
        self.last_page_start = self.coord

    def flush(self):
        self.op.set_base(self.base, self.base_id, update_layer_coordinates=False)


def find_annotation_of_reference(layer: Layer, reference: str):
    for ann in layer.annotations.values():
        if ann["reference"] == reference:
            return ann

def find_comparable_base_id(original_op, original_base_id, target_op):
    # for now we assume the bases have the same IDs in all the OPs
    # but that may not always be true
    return original_base_id
