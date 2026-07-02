import sys
from pathlib import Path
from config import *
from parser import *

if not len(PATH) :
    sys.exit("No path provided in config")



tab = parse_csv(PATH)

chemin = Path("outputs/tab.csv")
chemin2 = Path("outputs/tab.xslx")

chemin.parent.mkdir(parents=True, exist_ok=True)

tab.to_csv(chemin, index=False, encoding="utf-8")

tab.to_excel(chemin2, index=False)
