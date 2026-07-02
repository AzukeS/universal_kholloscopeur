import re
from config import MATIERES_ALIASES


DATE_PATTERN = re.compile(r"\d{1,2}/\d{1,2}(/\d{2,4})?")

def clean_cell(cell):
    if not isinstance(cell, str):
        return cell

    parts = cell.split("\n")

    for p in parts:
        if DATE_PATTERN.search(p):
            return p.strip()

    return cell
