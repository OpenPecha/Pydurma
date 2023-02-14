import logging

from openpecha.core.pecha import OpenPechaFS

from vulgatizer.vulgatizer_op_ocr import VulgatizerOPTibOCR



# change logging with:
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger('VulgatizerOPTibOCR')
#logger.setLevel(logging.DEBUG)
#logger = logging.getLogger('FDMPVulgaligner')
#logger.setLevel(logging.DEBUG)

def test_merger():
	op_output = OpenPechaFS("./data/I9B2646BE.opf")
	vulgatizer = VulgatizerOPTibOCR(op_output)
	# vulgatizer.add_op_witness(OpenPechaFS("../test/opfs/I001/I001.opf"))
	# vulgatizer.add_op_witness(OpenPechaFS("../test/opfs/I4DBEE949/I4DBEE949.opf"))
	# vulgatizer.add_op_witness(OpenPechaFS("../test/opfs/I8B1FB7BB/I8B1FB7BB.opf"))
	# vulgatizer.add_op_witness(OpenPechaFS("../test/opfs/IEA653111/IEA653111.opf"))
	# vulgatizer.add_op_witness(OpenPechaFS("../test/opfs/I002/I002.opf"))
	# vulgatizer.add_op_witness(OpenPechaFS("../test/opfs/I003/I003.opf"))

	vulgatizer.add_op_witness(OpenPechaFS("./data/opfs/I001/I001.opf"))
	vulgatizer.add_op_witness(OpenPechaFS("./data/opfs/I002/I002.opf"))
	vulgatizer.add_op_witness(OpenPechaFS("./data/opfs/I4DBEE949/I4DBEE949.opf"))
	vulgatizer.add_op_witness(OpenPechaFS("./data/opfs/I8B1FB7BB/I8B1FB7BB.opf"))
	vulgatizer.add_op_witness(OpenPechaFS("./data/opfs/IEA653111/IEA653111.opf"))
	vulgatizer.add_op_witness(OpenPechaFS("./data/opfs/I003/I003.opf"))
	vulgatizer.create_vulgate()

test_merger()