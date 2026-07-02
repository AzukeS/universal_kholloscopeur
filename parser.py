import pandas as pd
import re
from datetime import date, datetime
from utils import prefixes, dico_to_list, normalize_label
from heuristics import clean_cell
from config import FORMAT_ALIASES, DATE_FORMAT, WRITTEN_DATE_MIN_CHARACTERS, WRITTEN_MAY, WRITTEN_MARCH

def is_number_like(x):
    """
    Checks if a cell is a number, no matter its type.
    :param x: a cell
    :return: boolean if it is a number
    """
    if not isinstance(x, str):
        return False
    try:
        float(x.strip().replace(",", "."))
        return True
    except ValueError:
        return False

# def normalize_dates(df) :



# def ffill_strings_only(df):
#     """
#     Replaces NaN values with previous strings (e.g. professor names), avoiding ints for which blank cells actually exist.
#     :param df: 2d dataframe (pandas dataframe)
#     :return: filled dataframe
#     """
#
#     mask_str = ~ df.map(is_number_like) # we check which cells ARE NOT numbers
#     df_str_only = df.where(mask_str)
#     df_str_filled = df_str_only.ffill()
#     df = df.where(df.notna(), df_str_filled)
#
#     return df

def convert_date_to_usual_format(cell) :
    """
    Just converts a cell that contains a date with already xx/xx format to dd/mm/yyyy if possible.
    :param cell: cell from dataframe
    :return: a proper datetime string
    """
    if not isinstance(cell, str):
        return cell

    parts = re.findall(r"\d+", cell)
    if len(parts) not in (2, 3):
        return cell

    try:
        a, b = int(parts[0]), int(parts[1])

        if "dd/mm" in DATE_FORMAT.lower() or "dd-mm" in DATE_FORMAT.lower() :
            day, month = a, b
        elif "mm/dd" in DATE_FORMAT.lower() or  "mm-dd"  in DATE_FORMAT.lower() :
            month, day = a, b
        else:
            return cell  # impossible configuration

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

        return dt.strftime("%d/%m/%Y")

    except:
        return cell




def parse_date_cell(cell):
    """
    Converts a text date to dd/mm/yyyy if possible.
    Returns original cell otherwise.
    """

    if not isinstance(cell, str):
        return cell

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
    words = re.split(r"[^\w]+", text)
    numbers = re.findall(r"\d{1,4}", text)

    # Only numbers
    if len(numbers) in (2, 3) and not re.search(r"[a-z]", text) :
        return convert_date_to_usual_format(cell)

    # Extracting month
    month = None
    for w in words:
        if w in month_map:
            month = month_map[w]
            break

    if not month:
        return cell

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
        return cell

    # school year if not explicit
    if not year:
        now = datetime.now()
        school_end = 7  # juillet

        if month < school_end:
            year = now.year if now.month < school_end else now.year + 1
        else:
            year = now.year - 1 if now.month < school_end else now.year

    try:
        return datetime(year, month, day).strftime("%d/%m/%Y")
    except:
        return cell




def find_date_axis(df):
    """
    Return ('column', index) ou ('line', index) whether where are the dates.
    :param df: dataframe
    :return: date (string), index (int)"""

    # Score of each column
    col_scores = {}
    for col in df.columns:
        values = df[col]
        n_dates = sum(1 for v in values if parse_date_cell(v) is not v)
        ratio = n_dates / len(values) if len(values) else 0
        col_scores[col] = ratio

    # Score of each line
    row_scores = {}
    for idx in df.index:
        values = df.loc[idx]
        n_dates = sum(1 for v in values if parse_date_cell(v) is not v)
        ratio = n_dates / len(values) if len(values) else 0
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
    # df = ffill_strings_only(df)
    df = df.dropna(how="all")
    df = df.map(clean_cell)
    df = df.map(parse_date_cell)
    print(find_date_axis(df))

    return df
