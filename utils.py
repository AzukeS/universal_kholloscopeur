import unicodedata
import pandas as pd

CATEGORIES_INDEX = {
    "student": 0,
    "date": 1,
    "hour": 2,
    "weekday": 3,
    "room": 4,
    "teacher": 5,
    "subject": 6
}

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
    Converts pandas coordinates to excel cell coordinates
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


def apply_to_active_cells(active_cells, direction, categories_repartition, cell_coordinates, category):
    """
    Depending on if the category is vertical or horizontal, applies the value of the cell
    to all following active cells in the categories_repartition dataframe
    (i.e. cells after the source in the propagation direction, so an earlier category
    doesn't leak past a later one on the same row/column).
    """
    source = categories_repartition.iloc[cell_coordinates[0], cell_coordinates[1]]
    index = CATEGORIES_INDEX.get(category)

    if index is None:
        raise ValueError(f"Unknown category: {category}")
    if not isinstance(source, list) :
        return categories_repartition

    for row, col in active_cells:

        if (row, col) == cell_coordinates:
            continue

        if direction == "vertical" and col == cell_coordinates[1] and row > cell_coordinates[0]:
            categories_repartition.iloc[row, col][index] = source[-1]

        elif direction == "horizontal" and row == cell_coordinates[0] and col > cell_coordinates[1]:
            categories_repartition.iloc[row, col][index] = source[-1]

    return categories_repartition
import unicodedata
import pandas as pd

CATEGORIES_INDEX = {
    "student": 0,
    "date": 1,
    "hour": 2,
    "weekday": 3,
    "room": 4,
    "teacher": 5,
    "subject": 6
}

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
    Converts pandas coordinates to excel cell coordinates
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


def apply_to_active_cells(active_cells, direction, categories_repartition, cell_coordinates, category):
    """
    Depending on if the category is vertical or horizontal, applies the value of the cell
    to all following active cells in the categories_repartition dataframe
    (i.e. cells after the source in the propagation direction, so an earlier category
    doesn't leak past a later one on the same row/column).
    """
    source = categories_repartition.iloc[cell_coordinates[0], cell_coordinates[1]]
    index = CATEGORIES_INDEX.get(category)

    if index is None:
        raise ValueError(f"Unknown category: {category}")
    if not isinstance(source, list) :
        return categories_repartition

    for row, col in active_cells:

        if (row, col) == cell_coordinates:
            continue

        if direction == "vertical" and col == cell_coordinates[1] and row > cell_coordinates[0]:
            categories_repartition.iloc[row, col][index] = source[-1]

        elif direction == "horizontal" and row == cell_coordinates[0] and col > cell_coordinates[1]:
            categories_repartition.iloc[row, col][index] = source[-1]

    return categories_repartition
