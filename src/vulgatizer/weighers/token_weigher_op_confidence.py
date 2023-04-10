from bisect import bisect
from typing import List
from openpecha.core.layer import Layer, LayerEnum, PechaMetadata
from openpecha.core.annotations import OCRConfidence, BaseAnnotation

from vulgatizer.tokenizer import Token
from vulgatizer.utils.opf_utils import OPSegment, OPFragmentLayerAccessor
from vulgatizer.weighers.token_weigher import TokenWeigher


class OPConfidenceTokenWeigher(TokenWeigher):
	"""
	Returns the OCR confidence index as an integer between 0 and 100 for
	a token.
	"""

	def __init__(self, layer_accessors: List[OPFragmentLayerAccessor], value_for_gap: int = None, relative = True):
		super().__init__(relative)
		self.value_for_gap = value_for_gap
		self.layer_accessors = layer_accessors

	@staticmethod
	def get_lowest_confidence(layer_accessor: OPFragmentLayerAccessor, start: int, end: int) -> int:
		annotations = layer_accessor.get_annotations_in_range(start, end)
		res = None
		for annotation in annotations:
			c = annotation.confidence
			if c is not None:
				c_i = int(c * 100)
				if res is None or c_i < res:
					res = c_i
		return res

	def weigh(self, column: List[Token]) -> List[int]:
		weights = []
		for i, t in enumerate(column):
			if t is None:
				weights.append(self.value_for_gap)
				continue
			c = OPConfidenceTokenWeigher.get_lowest_confidence(self.layer_accessors[i], t[0], t[1])
			if c is None:
				c = 100
			weights.append(c)
		return weights
