from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parent

BO_SYLLIST_PATH = ROOT_PATH / 'res' / 'bo' / 'syllist.txt'

assert BO_SYLLIST_PATH.exists()
        