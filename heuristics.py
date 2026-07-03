import re
import sys
import pandas as pd
from datetime import datetime
from utils import match_matiere, normalize_label, excel_coord
from detector import classify_value, parse_time

def catch_students(df, categories_repartition) :
    """
    Parses the students tasks
    :param df: the original dataframe from the parsed csv file
    :param categories_repartition: the dataframe with categories repartition
    :return: the modified dataframe, the list of full locations of students cells, a boolean if students are sub-divided
    """
    active_cells = []
    sub_divide = False

    # regex
    simple_pattern = re.compile(r"^\d{1,2}$")
    subdiv_pattern = re.compile(r"^\d{1,2}[A-Za-z]$")

    # computes the rows with "semaine" (application cellule par cellule, pas colonne par colonne)
    normalized_df = df.astype(str).map(normalize_label)
    rows_with_semaine = normalized_df.apply(
        lambda row: row.str.contains("semaine", na=False).any(), axis=1
    )

    for col_idx in range(df.shape[1]):

        column = df.iloc[:, col_idx]

        # skip column if it contains "salle"
        if column.astype(str).apply(normalize_label).str.contains("salle", na=False).any():
            continue

        for row_idx in range(df.shape[0]):

            # skip row if it contains "semaine"
            if rows_with_semaine.iloc[row_idx]:
                continue

            val = df.iloc[row_idx, col_idx]

            if pd.isna(val):
                continue

            val_str = str(val).strip()

            if " " in val_str:
                continue

            # case: simple number
            if simple_pattern.match(val_str):
                active_cells.append((row_idx, col_idx))
                categories_repartition.iloc[row_idx, col_idx] = [df.iloc[row_idx, col_idx]]

            # case: subdivided (e.g. 12A)
            elif subdiv_pattern.match(val_str):
                active_cells.append((row_idx, col_idx))
                categories_repartition.iloc[row_idx, col_idx] = [df.iloc[row_idx, col_idx]]
                sub_divide = True
    return categories_repartition, active_cells, sub_divide

def propagate_dates(categories_repartition, df, date_line) :
    """
    Affects every group cell with the date it corresponds to
    :param categories_repartition: repartition table of attributes
    :param df: the original dataframe
    :param date_line: the line conatining the dates
    :return: the modified repartition dataframe
    """
    for i, date in enumerate(df.iloc[date_line]):
        if isinstance(date, datetime):
            for j in range(len(categories_repartition)):
                if categories_repartition.iloc[j, i] is not None:
                    cell = categories_repartition.iloc[j, i]
                    cell.append(date)

    return categories_repartition


def check_all_attributes_filled(categories_repartition, active_cells):
    """
    Checks if all the active cells have all the attributes filled.
    If not, returns an error, precising which attribute failed for which cell.

    :param categories_repartition: repartition table of attributes
    :param active_cells: list of (row_idx, col_idx) of active cells
    """
    required_attributes = ["student", "date", "hour", "weekday", "room", "subject", "teacher"]
    total_attributes = len(required_attributes)

    for row_idx, col_idx in active_cells:
        cell = categories_repartition.iloc[row_idx, col_idx] or []

        # fast path : if we got 7 attributes, the cell is OK
        if len(cell) == total_attributes:
            continue

        # Otherwise, we identify what is missing, in order
        found_attributes = {classify_value(v) for v in cell}
        missing_attributes = [a for a in required_attributes if a not in found_attributes]

        coord = excel_coord(row_idx, col_idx)
        sys.exit(
            f"Erreur : la cellule {coord} (ligne {row_idx}, colonne {col_idx}) "
            f"n'a pas reçu {'l\'attribut' if len(missing_attributes) == 1 else 'les attributs'} "
            f"suivant(s) : {', '.join(missing_attributes)}."
        )

def find_all_categories(df, date_line) :
    """
    Main heuristics function, creates a dataframe that shows every attribute (teacher, date, subject, hour) for every cell.
    :param df: the dataframe from the parsed csv file
    :param date_line: the line containing the dates of each week
    :return: the original dataframe and the repartition dataframe
    """
    categories_repartition = df.copy()
    categories_repartition[:] = None
    categories_repartition, active_cells, sub_divide = catch_students(df, categories_repartition)
    categories_repartition = propagate_dates(categories_repartition, df, date_line)
    check_all_attributes_filled(categories_repartition, active_cells)
    return categories_repartition