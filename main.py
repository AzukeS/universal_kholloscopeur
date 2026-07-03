import sys
from pathlib import Path
from config import *
from parser import *
from heuristics import find_all_categories

if not len(PATH) :
    sys.exit("No path provided in config")



tab, date_line = parse_csv(PATH)
categories_repartition =  find_all_categories(tab, date_line)


chemin = Path("outputs/tab.csv")
chemin2 = Path("outputs/tab.xslx")
chemin3 = Path("outputs/catégories.csv")
chemin4 = Path("outputs/catégories.xslx")


chemin.parent.mkdir(parents=True, exist_ok=True)

tab.to_csv(chemin, index=False, encoding="utf-8")

tab.to_excel(chemin2, index=False)
categories_repartition.to_csv(chemin3, index=False, encoding="utf-8")

categories_repartition.to_excel(chemin4, index=False)

