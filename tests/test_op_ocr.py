import logging
from pathlib import Path

from openpecha.core.pecha import OpenPechaFS

from vulgatizer.vulgatizer_op_ocr import VulgatizerOPTibOCR
from vulgatizer.vulgatizer_plain_text import VulgatizerPlainText



# change logging with:
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger('VulgatizerOPTibOCR')
#logger.setLevel(logging.DEBUG)
#logger = logging.getLogger('FDMPVulgaligner')
#logger.setLevel(logging.DEBUG)

def test_vulgatizer_op():
	op_output = OpenPechaFS("./data/vulgate/I9B2646BE.opf")
	vulgatizer = VulgatizerOPTibOCR(op_output)

	vulgatizer.add_op_witness(OpenPechaFS("./data/I0001/I0001.opf"))
	vulgatizer.add_op_witness(OpenPechaFS("./data/I0002/I0002.opf"))
	vulgatizer.add_op_witness(OpenPechaFS("./data/I0003/I0003.opf"))
	vulgatizer.add_op_witness(OpenPechaFS("./data/I0004/I0004.opf"))
	vulgatizer.add_op_witness(OpenPechaFS("./data/I0005/I0005.opf"))
	
	vulgatizer.create_vulgate()


def test_vulgatizer_plain_text():
	op_output = OpenPechaFS("./data/vulgate/I9B2646B7.opf")
	vulgatizer = VulgatizerPlainText(op_output)
	vulgatizer.add_witness(Path("./data/I0001/I0001.opf/base/95E3.txt"))
	vulgatizer.add_witness(Path("./data/I0002/I0002.opf/base/95E3.txt"))
	vulgatizer.add_witness(Path("./data/I0003/I0003.opf/base/95E3.txt"))
	vulgatizer.add_witness(Path("./data/I0004/I0004.opf/base/95E3.txt"))
	vulgatizer.add_witness(Path("./data/I0005/I0005.opf/base/95E3.txt"))
	
	vulgatizer.create_vulgate()
