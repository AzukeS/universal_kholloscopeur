import re
from datetime import time, datetime
from utils import normalize_label, is_empty
from config import MATIERES_ALIASES




def match_matiere(x:str):
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



def parse_time(cell):
    """
    :param cell: A dataframe cell
    :return: The string representing a time or None if the cell doesn't have a time
    """
    if not isinstance(cell, str):
        return None

    cell = cell.lower().strip()

    # special case
    if "midi" in cell:
        return time(12, 0)

    # HH:MM format
    match = re.search(r"\b(\d{1,2}):(\d{1,2})\b", cell)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            return time(h, m)
        return None

    # HhMM or Hh format
    match = re.search(r"\b(\d{1,2})h(\d{0,3})\b", cell)
    if match:
        h = int(match.group(1))
        m_str = match.group(2)

        if not (0 <= h <= 23):
            return None

        if m_str == "":
            m = 0
        else:
            m = int(m_str)
            if m > 59:
                # corrects strange cases with 0s
                m = int(m_str.lstrip("0") or "0")

        if 0 <= m <= 59:
            return time(h, m)

    return None



def classify_value(value):
    """
    Gives the category to which the value belongs (string, e.g. "hour") or None if it doesn't.
    :param value: an attribute in an active cell
    :return: atribute category
    """
    if isinstance(value, datetime):
        return "date"

    if isinstance(value, time):
        return "hour"

    val_str = str(value).strip()

    # student : "12" or "12A"
    if re.match(r"^\d{1,2}$", val_str) or re.match(r"^\d{1,2}[A-Za-z]$", val_str):
        return "student"

    # weekday
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    if val_str.lower() in jours:
        return "weekday"

    if match_matiere(val_str) is not None:
        return "subject"

    # salle
    if "labo" in normalize_label(val_str) or re.search(r"\b([A-Za-z]\d{2,3}|\d{3})\b", val_str):
        return "room"

    # prof : "M." / "Mme." + {. / space} + word
    if re.search(r"^Mm?e?[.\s]\s?[A-Za-zÀ-ÿ]+$", val_str):
        return "teacher"

    return None

parsers = {
    "hour": parse_time,
    # "weekday": parse_weekday,
    # "subject": parse_subject,
    # "teacher": parse_teacher,
    # "room": parse_room,
}

def propagate_line(line, parser):
    """
    Propagates the category to the following None (empty) cells
    """

    propagated = []
    last_valid = False

    for cell in line:
        parsed = parser(cell)

        if parsed is not None: # cell contains a valid category
            last_valid = True
            propagated.append(True)

        elif is_empty(cell):
            propagated.append(last_valid)

        else:
            # cellule non vide MAIS pas de la catégorie
            last_valid = False
            propagated.append(False)

    return propagated


def find_direction(category, df) :
    """
    Determine how a category propagates from a given cell in a DataFrame.

    Categories are assumed to be aligned either along a row or a column:
        - If most occurrences of the category are in the same column,
        the category applies horizontally (across rows).
        - If most occurrences are in the same row,
        the category applies vertically (down columns).
    (Not the most intuitive but it is easier that way)
    :param category: The category to parse
    :param df: The original dataframe parsed from CSV file
    :return: "vertical" or "horizontal", depending on the dominant direction of the category around the cell (i.e., perpendicular to the densest axis).
    """

    parser = parsers.get(category)

    row_scores = []
    for i in range(df.shape[0]):
        row = df.iloc[i]
        propagated = propagate_line(row, parser)
        row_scores.append(sum(propagated) / len(propagated))

    col_scores = []
    for j in range(df.shape[1]):
        col = df.iloc[:, j]
        propagated = propagate_line(col, parser)
        col_scores.append(sum(propagated) / len(propagated))

    row_strength = max(row_scores)
    col_strength = max(col_scores)

    return "vertical" if row_strength > col_strength else "horizontal"