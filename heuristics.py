import re
import sys
import pandas as pd
from datetime import datetime, timedelta
from utils import normalize_label, excel_coord, apply_to_active_cells, is_empty, CATEGORIES_INDEX
from detector import classify_value, parse_time, parse_weekday, parse_teacher, parse_room, parse_subject, find_direction, catch_label_coordinates

def catch_students(df, categories_repartition) :
    """
    Parses the students tasks, and initializes them as 7-element lists
    :param df: the original dataframe from the parsed csv file
    :param categories_repartition: the dataframe with categories repartition
    :return: the modified dataframe, the list of full locations of students cells, a boolean if students are sub-divided
    """
    active_cells = []
    sub_divide = False

    # regex
    simple_pattern = re.compile(r"^\d{1,2}$")
    subdiv_pattern = re.compile(r"^\d{1,2}[A-Za-z]$")

    # computes the rows with "semaine" (cell by cell)
    normalized_df = df.astype(str).map(normalize_label)
    rows_with_semaine = normalized_df.apply(
        lambda row: row.str.contains("semaine", na=False).any(), axis=1
    )

    for col_idx in range(df.shape[1]):


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
                categories_repartition.iloc[row_idx, col_idx] = [df.iloc[row_idx, col_idx], None, None, None, None, None, None]

            # case: subdivided (e.g. 12A)
            elif subdiv_pattern.match(val_str):
                active_cells.append((row_idx, col_idx))
                categories_repartition.iloc[row_idx, col_idx] = [df.iloc[row_idx, col_idx], None, None, None, None, None, None]
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
    index = CATEGORIES_INDEX.get("date")
    for i, date in enumerate(df.iloc[date_line]):
        if isinstance(date, datetime):
            for j in range(len(categories_repartition)):
                cell = categories_repartition.iloc[j, i]

                if isinstance(cell, list) and len(cell) == len(CATEGORIES_INDEX) :
                    cell[index] = date

    return categories_repartition


def catch_hours(df, categories_repartition, active_cells):
    """
    Parses the hours of the tasks for the whole df
    :param df: The dataframe from the parsed csv file
    :param categories_repartition: The dataframe with categories repartition
    :return: the modified dataframe with added hour of the kholle for each active cell
    """
    direction = find_direction("hour", df)

    for col_idx in range(df.shape[1]):
        for row_idx in range(df.shape[0]):
            cell = df.iloc[row_idx, col_idx]
            hour = parse_time(cell)

            if hour is not None:

                current = categories_repartition.iloc[row_idx, col_idx]
                if not isinstance(current, list):
                    categories_repartition.iloc[row_idx, col_idx] = [hour]
                else:
                    current.append(hour)

                # cells modified in the loop
                modified_coords = [(row_idx, col_idx)]

                if direction == "horizontal":
                    i = row_idx + 1
                    while i < df.shape[0] and pd.isna(df.iloc[i, col_idx]):
                        target = categories_repartition.iloc[i, col_idx]
                        if not isinstance(target, list):
                            categories_repartition.iloc[i, col_idx] = [hour]
                        else:
                            target.append(hour)
                        modified_coords.append((i, col_idx))
                        i += 1

                elif direction == "vertical":
                    j = col_idx + 1
                    while j < df.shape[1] and pd.isna(df.iloc[row_idx, j]):
                        target = categories_repartition.iloc[row_idx, j]
                        if not isinstance(target, list):
                            categories_repartition.iloc[row_idx, j] = [hour]
                        else:
                            target.append(hour)
                        modified_coords.append((row_idx, j))
                        j += 1

                # apply_to_active_cells for all modified cells
                for coords in modified_coords:
                    apply_to_active_cells(active_cells, direction, categories_repartition, coords, "hour")


def catch_weekday(df, categories_repartition, active_cells):
    """
    Parses the weekday of each task for the whole df
    :param df: The dataframe from the parsed csv file
    :param categories_repartition: The dataframe with categories repartition
    :return: the modified dataframe with added weekday of the kholle for each active cell
    """
    direction = find_direction("weekday", df)

    for col_idx in range(df.shape[1]):
        for row_idx in range(df.shape[0]):
            cell = df.iloc[row_idx, col_idx]
            weekday = parse_weekday(cell)

            if weekday is not None:

                current = categories_repartition.iloc[row_idx, col_idx]
                if not isinstance(current, list):
                    categories_repartition.iloc[row_idx, col_idx] = [weekday]
                else:
                    current.append(weekday)

                # cells modified in the loop
                modified_coords = [(row_idx, col_idx)]

                if direction == "horizontal":
                    i = row_idx + 1
                    while i < df.shape[0] and pd.isna(df.iloc[i, col_idx]):
                        target = categories_repartition.iloc[i, col_idx]
                        if not isinstance(target, list):
                            categories_repartition.iloc[i, col_idx] = [weekday]
                        else:
                            target.append(weekday)
                        modified_coords.append((i, col_idx))
                        i += 1

                elif direction == "vertical":
                    j = col_idx + 1
                    while j < df.shape[1] and pd.isna(df.iloc[row_idx, j]):
                        target = categories_repartition.iloc[row_idx, j]
                        if not isinstance(target, list):
                            categories_repartition.iloc[row_idx, j] = [weekday]
                        else:
                            target.append(weekday)
                        modified_coords.append((row_idx, j))
                        j += 1

                # apply_to_active_cells for all modified cells
                for coords in modified_coords:
                    apply_to_active_cells(active_cells, direction, categories_repartition, coords, "weekday")


def catch_room(df, categories_repartition, active_cells):
    """
    Parses the room of each task for the whole df
    :param df: The dataframe from the parsed csv file
    :param categories_repartition: The dataframe with categories repartition
    :return: the modified dataframe with added room of the kholle for each active cell
    """
    direction = find_direction("room", df)
    label_coordinates = catch_label_coordinates(df, "room", direction)

    for col_idx in range(df.shape[1]):
        for row_idx in range(df.shape[0]):
            cell = df.iloc[row_idx, col_idx]
            room = parse_room(cell, (row_idx, col_idx), label_coordinates, direction)

            if room is not None:

                current = categories_repartition.iloc[row_idx, col_idx]
                if not isinstance(current, list):
                    categories_repartition.iloc[row_idx, col_idx] = [room]
                else:
                    current.append(room)

                # cells modified in the loop
                modified_coords = [(row_idx, col_idx)]

                current_room = room

                if direction == "horizontal":
                    i = row_idx + 1

                    while i < df.shape[0]:
                        cell_i = df.iloc[i, col_idx]
                        detected = parse_room(cell_i, (i, col_idx), label_coordinates, direction)

                        if detected is not None:
                            break

                        if pd.isna(cell_i):
                            new_room = current_room
                        else:
                            new_room = cell_i

                        target = categories_repartition.iloc[i, col_idx]
                        if not isinstance(target, list):
                            categories_repartition.iloc[i, col_idx] = [new_room]
                        else:
                            target.append(new_room)

                        modified_coords.append((i, col_idx))

                        current_room = new_room
                        i += 1

                elif direction == "vertical":
                    j = col_idx + 1

                    while j < df.shape[1]:
                        cell_j = df.iloc[row_idx, j]
                        detected = parse_room(cell_j, (row_idx, j), label_coordinates, direction)

                        if detected is not None:
                            break

                        if pd.isna(cell_j):
                            new_room = current_room
                        else:
                            new_room = cell_j

                        target = categories_repartition.iloc[row_idx, j]
                        if not isinstance(target, list):
                            categories_repartition.iloc[row_idx, j] = [new_room]
                        else:
                            target.append(new_room)

                        modified_coords.append((row_idx, j))

                        current_room = new_room
                        j += 1

                # apply_to_active_cells for all modified cells
                for coords in modified_coords:
                    apply_to_active_cells(active_cells, direction, categories_repartition, coords, "room")


def catch_teacher(df, categories_repartition, active_cells):
    """
    Parses the teacher of each task for the whole df
    :param df: The dataframe from the parsed csv file
    :param categories_repartition: The dataframe with categories repartition
    :return: the modified dataframe with added teacher of the kholle for each active cell
    """
    direction = find_direction("teacher", df)
    label_coordinates = catch_label_coordinates(df, "teacher", direction)

    for col_idx in range(df.shape[1]):
        for row_idx in range(df.shape[0]):
            cell = df.iloc[row_idx, col_idx]
            teacher = parse_teacher(cell, (row_idx, col_idx), label_coordinates, direction)

            if teacher is not None:

                current = categories_repartition.iloc[row_idx, col_idx]
                if not isinstance(current, list):
                    categories_repartition.iloc[row_idx, col_idx] = [teacher]
                else:
                    current.append(teacher)

                # cells modified in the loop
                modified_coords = [(row_idx, col_idx)]

                current_teacher = teacher

                if direction == "horizontal":
                    i = row_idx + 1

                    while i < df.shape[0]:
                        cell_i = df.iloc[i, col_idx]
                        detected = parse_teacher(cell_i, (i, col_idx), label_coordinates, direction)

                        if detected is not None:
                            break

                        if pd.isna(cell_i):
                            new_teacher = current_teacher
                        else:
                            new_teacher = cell_i

                        target = categories_repartition.iloc[i, col_idx]
                        if not isinstance(target, list):
                            categories_repartition.iloc[i, col_idx] = [new_teacher]
                        else:
                            target.append(new_teacher)

                        modified_coords.append((i, col_idx))

                        current_teacher = new_teacher
                        i += 1

                elif direction == "vertical":
                    j = col_idx + 1

                    while j < df.shape[1]:
                        cell_j = df.iloc[row_idx, j]
                        detected = parse_teacher(cell_j, (row_idx, j), label_coordinates, direction)

                        if detected is not None:
                            break

                        if pd.isna(cell_j):
                            new_teacher = current_teacher
                        else:
                            new_teacher = cell_j

                        target = categories_repartition.iloc[row_idx, j]
                        if not isinstance(target, list):
                            categories_repartition.iloc[row_idx, j] = [new_teacher]
                        else:
                            target.append(new_teacher)

                        modified_coords.append((row_idx, j))

                        current_teacher = new_teacher
                        j += 1

                # apply_to_active_cells for all modified cells
                for coords in modified_coords:
                    apply_to_active_cells(active_cells, direction, categories_repartition, coords, "teacher")


def catch_subject(df, categories_repartition, active_cells):
    """
    Parses the subject of each task for the whole df
    :param df: The dataframe from the parsed csv file
    :param categories_repartition: The dataframe with categories repartition
    :return: the modified dataframe with added subject of the kholle for each active cell
    """
    direction = find_direction("subject", df)

    for col_idx in range(df.shape[1]):
        for row_idx in range(df.shape[0]):
            cell = df.iloc[row_idx, col_idx]
            subject = parse_subject(cell)

            if subject is not None:

                current = categories_repartition.iloc[row_idx, col_idx]
                if not isinstance(current, list):
                    categories_repartition.iloc[row_idx, col_idx] = [subject]
                else:
                    current.append(subject)

                # cells modified in the loop
                modified_coords = [(row_idx, col_idx)]

                if direction == "horizontal":
                    i = row_idx + 1
                    while i < df.shape[0] and pd.isna(df.iloc[i, col_idx]):
                        target = categories_repartition.iloc[i, col_idx]
                        if not isinstance(target, list):
                            categories_repartition.iloc[i, col_idx] = [subject]
                        else:
                            target.append(subject)
                        modified_coords.append((i, col_idx))
                        i += 1

                elif direction == "vertical":
                    j = col_idx + 1
                    while j < df.shape[1] and pd.isna(df.iloc[row_idx, j]):
                        target = categories_repartition.iloc[row_idx, j]
                        if not isinstance(target, list):
                            categories_repartition.iloc[row_idx, j] = [subject]
                        else:
                            target.append(subject)
                        modified_coords.append((row_idx, j))
                        j += 1

                # apply_to_active_cells for all modified cells
                for coords in modified_coords:
                    apply_to_active_cells(active_cells, direction, categories_repartition, coords, "subject")

def check_all_attributes_filled(categories_repartition, active_cells):
    """
    Checks if all the active cells have all the attributes filled.
    If not, returns an error, precising which attribute failed for which cell.

    :param categories_repartition: repartition table of attributes
    :param active_cells: list of (row_idx, col_idx) of active cells
    """
    required_attributes = ["student", "date", "hour", "weekday", "room", "teacher", "subject"]

    for row_idx, col_idx in active_cells:
        cell = categories_repartition.iloc[row_idx, col_idx] or []

        # fast path : if we got 7 attributes, the cell is OK
        None_counter = 0
        for category in cell:
            if category is None :
                None_counter += 1
        if None_counter == 0:
            continue

        # Otherwise, we identify what is missing, in order
        found_attributes = {classify_value(v) for v in cell}
        missing_attributes = [a for a in required_attributes if a not in found_attributes]

        coord = excel_coord(row_idx, col_idx)
        missing_word = "l'attribut" if len(missing_attributes) == 1 else "les attributs"
        sys.exit(
            f"Erreur : la cellule {coord} (ligne {row_idx}, colonne {col_idx}) "
            f"n'a pas pu recevoir {missing_word} "
            f"suivant(s) : {', '.join(missing_attributes)}."
        )


def find_all_categories(df, date_line) :
    """
    Main heuristics function, creates a dataframe that shows every attribute (in the order : student number, date of the monday, hour, weekday, teacher, subject) for every cell.
    :param df: the dataframe from the parsed csv file
    :param date_line: the line containing the dates of each week
    :return: the original dataframe and the repartition dataframe
    """
    categories_repartition = pd.DataFrame(
        None,
        index=df.index,
        columns=df.columns,
        dtype=object
    )
    categories_repartition, active_cells, sub_divide = catch_students(df, categories_repartition)
    categories_repartition = propagate_dates(categories_repartition, df, date_line)
    catch_hours(df, categories_repartition, active_cells)
    catch_weekday(df, categories_repartition, active_cells)
    catch_room(df, categories_repartition, active_cells)
    catch_teacher(df, categories_repartition, active_cells)
    catch_subject(df, categories_repartition, active_cells)

    check_all_attributes_filled(categories_repartition, active_cells)
    return categories_repartition, active_cells, sub_divide