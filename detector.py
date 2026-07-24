import re
from datetime import time, datetime
from utils import normalize_label, is_empty
from config import *




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


def parse_weekday(cell) -> int | None:
    """
    Extracts the days past monday of the day contained in the cell
    :param cell: A cell from a dateframe
    :return: an int (how many days past monday) or None if the cell doesn't contain a day
    """
    if not isinstance(cell, str):
        return None

    cell = cell.lower().strip()
    for canon, aliases in WEEK_DAYS.items():
        for alias in aliases:
            for word in cell.split():
                word = word.strip(".,;:-")
                if word == alias:
                    return int(canon)
    return None


def parse_teacher(cell, cell_coordinates, label_coordinates, direction) -> str | None:
    """
    Returns the room contained in the cell, or None if the cell doesn't contain a room.
    It should be either contained in SPECIAL_ROOMS (config.py) or to the format letter + 2/3 digits or 3 digits.
    :param cell: A cell from the dataframe.
    :param cell_coordinates: A tuple with two integers representing the cell's coordinates
    :param label_coordinates: A list with all the occurences of the room label
    :param direction: The way the category room propagates to cells (horizontaly or vertically)
    :return: the room (string) or None.
    """
    if not isinstance(cell, str):
        return None
    cell = cell.strip()
    cell = cell.strip(".,;:-")
    if normalize_label(cell) in SPECIAL_ROOMS:
        return cell
    # letter + 2/3 digits format or 3 digits (e.g. D300, B23, or 234)
    elif re.search(r"\b([A-Za-z]\d{2,3}|\d{3})\b", normalize_label(cell)):
        return cell
    elif direction == "vertical" and cell_coordinates[0] in label_coordinates :
        return cell
    elif direction == "horizontal" and cell_coordinates[1] in label_coordinates :
        return cell
    return None


def parse_teacher(cell, cell_coordinates, label_coordinates, direction) -> str | None:
    """
    Returns the teacher contained in the cell, or None if the cell doesn't contain a teacher's name.
    Should be to the format M/Mme/Mr/Mrs + ("."/ "") + " "
    :param cell: A cell from the dataframe.
    :param cell_coordinates: A tuple with two integers representing the cell's coordinates
    :param label_coordinates: A list with all the occurences of the room label
    :param direction: The way the category room propagates to cells (horizontaly or vertically)
    :return: the teacher (string) or None.
    """
    if not isinstance(cell, str):
        return None
    cell = cell.strip()
    cell = cell.strip(".,;:-()[]{}")
    titles_pattern = "|".join(map(re.escape, TEACHER_TITLES))

    stop_words = [
        "et",
        "salle",
        "groupe",
        "classe",
        "absent",
        "absente",
        "présent",
        "présente",
    ]

    stop_pattern = "|".join(stop_words)

    pattern = (
        rf"(?<![a-zà-ÿ])({titles_pattern})\.?\s+"
        rf"[a-zà-ÿ]+(?:\.[a-zà-ÿ]+)*\.?"
        rf"(?:['-][a-zà-ÿ]+\.?| [a-zà-ÿ]+\.?)*?"
        rf"(?=\s+(?:{stop_pattern})\b|\s+(?:{titles_pattern})\.?\s+|"
        rf"\s*[/+,]\s*|\s*[\(\)\[\]]|[\s\d\W]*$)"
    )
    matches = re.finditer(pattern, cell, flags=re.IGNORECASE)

    teachers = [match.group(0) for match in matches]

    if teachers:
        return " / ".join(teachers)
    elif direction == "vertical" and cell_coordinates[0] in label_coordinates :
        return cell
    elif direction == "horizontal" and cell_coordinates[1] in label_coordinates :
        return cell
    return None


def parse_subject(cell) -> str | None:
    """
    Returns the subject contained in the cell, or None if the cell doesn't contain a subject name.
    It should be either contained in MATIERES_ALIASES (config.py).
    :return: the subject (string) or None.
    """
    if not isinstance(cell, str):
        return None
    for key, aliases in MATIERES_ALIASES.items():
        for word in cell.split():
            if normalize_label(word) in aliases:
                return key


def classify_value(value) -> str | None:
    """
    Gives the category to which the value belongs -probably, not as precise as dedicated parsers- (string, e.g. "hour") or None if it doesn't.
    :param value: an attribute in an active cell
    :return: atribute category
    """
    if isinstance(value, datetime):
        return "date"

    if isinstance(value, time):
        return "hour"

    if isinstance(value, int):
        return "weekday"

    val_str = str(value).strip()

    # student : "12" or "12A"
    if re.match(r"^\d{1,2}$", val_str) or re.match(r"^\d{1,2}[A-Za-z]$", val_str):
        return "student"

    # subject
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
    "weekday": parse_weekday,
    "subject": parse_subject,
    "teacher": parse_teacher,
    "room": parse_teacher,
}

def propagate_line(line, parser):
    """
    Propagates the category to the following None (empty) cells
    """

    propagated = []
    last_valid = False

    if parser not in [parse_teacher, parse_teacher]:
        for cell in line:
            parsed = parser(cell)

            if parsed is not None: # cell contains a valid category
                last_valid = True
                propagated.append(True)

            elif is_empty(cell):
                propagated.append(last_valid)

            else:
                # cell not empty but not valid
                last_valid = False
                propagated.append(False)
    else :
        for cell in line:
            parsed = parser(cell, None, None, None)

            if parsed is not None: # cell contains a valid category
                last_valid = True
                propagated.append(True)

            elif is_empty(cell):
                propagated.append(last_valid)

            else:
                # cell not empty but not valid
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
    (Not the most intuitive at first glance but it is easier that way)
    :param category: The category to parse
    :param df: The original dataframe parsed from CSV file
    :return: "vertical" or "horizontal", depending on the dominant direction of the category
             around the cell (i.e., perpendicular to the densest axis).
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


def catch_label_coordinates(df, label, direction):
    """
    Finds the labels in the dataframe and returns their coordinates
    :param df: The original dataframe parsed from CSV file
    :param label: The label to search
    :param direction: The direction of how the category is propagated to cells (either "vertical" or "horizontal")
    :return: A list with 3 elements.
    """

    label_coords = {
        "coords": [],
        "common": None
    }
    for col_idx in range(df.shape[1]):
        for row_idx in range(df.shape[0]):
            cell = df.iloc[row_idx, col_idx]
            if label == "room" and normalize_label(cell) in ROOM_LABELS:
                if direction == "vertical":
                    if label_coords["common"] is None:
                        label_coords["common"] = col_idx
                    if col_idx == label_coords["common"]:
                        label_coords["coords"].append(row_idx)
                elif direction == "horizontal":
                    if label_coords["common"] is None:
                        label_coords["common"] = row_idx
                    if row_idx == label_coords["common"]:
                        label_coords["coords"].append(col_idx)
            elif label == "teacher" and normalize_label(cell) in TEACHER_LABELS:
                if direction == "vertical":
                    if label_coords["common"] is None:
                        label_coords["common"] = col_idx
                    if col_idx == label_coords["common"]:
                        label_coords["coords"].append(row_idx)
                elif direction == "horizontal":
                    if label_coords["common"] is None:
                        label_coords["common"] = row_idx
                    if row_idx == label_coords["common"]:
                        label_coords["coords"].append(col_idx)
            elif label == "subject" and normalize_label(cell) in SUBJECTS_LABELS:
                if direction == "vertical":
                    if label_coords["common"] is None:
                        label_coords["common"] = col_idx
                    if col_idx == label_coords["common"]:
                        label_coords["coords"].append(row_idx)
                elif direction == "horizontal":
                    if label_coords["common"] is None:
                        label_coords["common"] = row_idx
                    if row_idx == label_coords["common"]:
                        label_coords["coords"].append(col_idx)
    return label_coords["coords"]
