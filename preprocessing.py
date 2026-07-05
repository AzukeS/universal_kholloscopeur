import pandas as pd
import re
from datetime import date, datetime
from utils import prefixes, dico_to_list, normalize_label
from config import FORMAT_ALIASES, DATE_FORMAT, WRITTEN_DATE_MIN_CHARACTERS, WRITTEN_MAY, WRITTEN_MARCH

DATE_PATTERN = re.compile(r"\d{1,2}/\d{1,2}(/\d{2,4})?")


def clean_cell(cell):
    if isinstance(cell, tuple):
        cell = cell[0]

    if not isinstance(cell, str):
        return cell

    parts = cell.split("\n")

    candidates = [p.strip() for p in parts if DATE_PATTERN.search(p)]

    if candidates:
        return "\n".join(parts)

    return cell


def convert_date_to_usual_format(cell) :
    """
    Just converts a cell that contains a date with already xx/xx format to dd/mm/yyyy if possible.
    :param cell: cell from dataframe
    :return: a proper datetime string
    """
    if not isinstance(cell, str):
        return cell, False

    parts = re.findall(r"\d+", cell)
    if len(parts) < 2:
        return cell, False

    try:
        a, b = int(parts[0]), int(parts[1])

        if "dd/mm" in DATE_FORMAT.lower() or "dd-mm" in DATE_FORMAT.lower() :
            day, month = a, b
        elif "mm/dd" in DATE_FORMAT.lower() or  "mm-dd"  in DATE_FORMAT.lower() :
            month, day = a, b
        else:
            return cell, False  # impossible configuration

        if len(parts) == 3:
            year = int(parts[2])
            if year < 100:
                year += 2000
        else:
            now = datetime.now()
            school_end = 7  # juillet

            if month < school_end:
                year = now.year if now.month < school_end else now.year + 1
            else:
                year = now.year - 1 if now.month < school_end else now.year

        dt = datetime(year, month, day)

        return dt, True

    except:
        return cell, False




def parse_date_cell(cell):
    """
    Converts a text date to dd/mm/yyyy if possible.
    Returns original cell otherwise.
    """

    if isinstance(cell, tuple):
        cell = cell[0]
    if not isinstance(cell, str):
        return cell, False

    text = normalize_label(cell)

    # mapping alias -> month
    if WRITTEN_DATE_MIN_CHARACTERS > 2 :
        month_map = {
        normalize_label(alias)[:i]: month
        for month, aliases in FORMAT_ALIASES.items()
        for alias in aliases
        for i in range(WRITTEN_DATE_MIN_CHARACTERS, len(alias) +1)
        }
    else :
        month_map = {
        normalize_label(alias)[:i]: month
        for month, aliases in FORMAT_ALIASES.items()
        for alias in aliases
        for i in range(2, len(alias) + 1)
        }
        # Litigious cases of mars vs mai, juin vs juillet
        month_map.update({
            WRITTEN_MARCH: 3,
            WRITTEN_MAY:5,
        })
    words = [normalize_label(w) for w in re.split(r"[^a-zA-Z0-9]+", text)]
    numbers = re.findall(r"\d{1,4}", text)

    # Only numbers
    date_match = re.search(r"\d{1,2}/\d{1,2}(?:/\d{2,4})?", cell)

    if date_match:
        res, ok = convert_date_to_usual_format(date_match.group())
        if ok:
            return res, True
    # Extracting month
    month = None
    for w in words:
        if w in month_map:
            month = month_map[w]
            break

    if not month:
        return cell, False

    # extracting the day and the year
    day = None
    year = None

    for n in numbers:
        n_int = int(n)
        if n_int > 31:
            year = n_int if n_int > 100 else 2000 + n_int
        elif not day:
            day = n_int

    if not day:
        return cell, False

    # school year if not explicit
    if not year:
        now = datetime.now()
        school_end = 7  # juillet

        if month < school_end:
            year = now.year if now.month < school_end else now.year + 1
        else:
            year = now.year - 1 if now.month < school_end else now.year

    try:
        return datetime(year, month, day), True
    except:
        return cell, False




def find_date_axis(df, mask):
    """
    Return ('column', index) ou ('line', index) whether where are the dates.
    :param df: dataframe
    :return: date (string), index (int)"""

    col_scores = {}
    for col in df.columns:
        values = df[col]
        ratio = mask[col].sum() / len(values)
        col_scores[col] = ratio

    row_scores = {}
    for idx in df.index:
        values = df.loc[idx]
        ratio = mask.loc[idx].sum() / len(values)
        row_scores[idx] = ratio
    best_col = max(col_scores, key=col_scores.get)
    best_row = max(row_scores, key=row_scores.get)

    if col_scores[best_col] >= row_scores[best_row]:
        return ("column", best_col, col_scores[best_col])
    else:
        return ("line", best_row, row_scores[best_row])


def parse_csv(PATH):
    """
    Main function for parsing the csv file.
    :param PATH: path to csv file
    :return: the correct-filled dataframe
    """
    df = pd.read_csv(PATH, header=None)
    df = df.dropna(how="all")
    df = df.map(clean_cell)
    parsed = df.map(parse_date_cell)
    df = parsed.map(lambda x: x[0])
    mask = parsed.map(lambda x: x[1])

    date_coordinate = find_date_axis(df, mask)
    if date_coordinate[0] == "column" :
        df = df.transpose()

    return [df, date_coordinate[1]]

