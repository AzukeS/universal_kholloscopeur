import unicodedata
import re
from config import MATIERES_ALIASES, FORMAT_ALIASES
from datetime import datetime, time, date


def is_empty(cell):
    return pd.isna(cell) or (isinstance(cell, str) and cell.strip() == "")

def normalize_label(x):
    """
    Converts the label of the cell to a format without capitalization, accents or special characters
    :param x: a cell label
    :return: the normalized cell label
    """
    if not isinstance(x, str):
        return x
    s = x.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = " ".join(s.split())
    return s


def match_matiere(x):
    """
    Gives the subject listed in MATIERES_ALIASES which corresponds to the cell label
    :param x: a cell label
    :return: the subject
    """
    key = normalize_label(x)
    words = set(key.split())

    for canon, aliases in MATIERES_ALIASES.items():
        for alias in aliases:
            alias_words = set(alias.split())
            if alias_words.issubset(words):
                return canon
    return None


def prefixes(word):
    """
    Returns a list of prefixes of word with at least two letters
    :param word: a word
    :return: the list of prefixes
    """
    return [word[:i] for i in range(2, len(word) + 1)]

def dico_to_list(dico) :
    list = []
    for k in dico:
        list += dico[k]
    return list

def excel_coord(row_idx, col_idx):
    """
    Converts pandas coordonates to excel cell coordinates
    :param row_idx: line index (0-based)
    :param col_idx: column index (0-based)
    :return: chaîne du type "B3"
    """
    col = col_idx + 1
    letters = ""
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row_idx + 1}"
