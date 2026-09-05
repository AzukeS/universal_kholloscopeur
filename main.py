import sys
from pathlib import Path
import config
from preprocessing import normalize_all_config, parse_csv
from heuristics import find_all_categories
from normalizer import main_normalizer, file_creator


if not config.PATH:
    sys.exit("No path provided in config")


normalize_all_config()
tab, date_line = parse_csv(config.PATH)
categories_repartition, active_cells, sub_divide =  find_all_categories(tab, date_line)
main_normalizer(categories_repartition, active_cells)
file_creator(categories_repartition, active_cells, sub_divide)


# debug
export_dir = Path(config.EXPORT_PATH)
export_dir.mkdir(parents=True, exist_ok=True)

chemin = export_dir / "tab.csv"
chemin2 = export_dir / "tab.xlsx"
chemin3 = export_dir / "catégories.csv"
chemin4 = export_dir / "catégories.xlsx"

tab.to_csv(chemin, index=False, encoding="utf-8")
tab.to_excel(chemin2, index=False)
categories_repartition.to_csv(chemin3, index=False, encoding="utf-8")
categories_repartition.to_excel(chemin4, index=False)

