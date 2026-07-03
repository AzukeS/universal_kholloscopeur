import re
from datetime import time, datetime, date
from utils import normalize_label, match_matiere


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
        return "12:00"


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