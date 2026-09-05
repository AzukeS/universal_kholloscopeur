import re
import csv
from datetime import datetime, timedelta

import config
from utils import CATEGORIES_INDEX
from pathlib import Path


FINAL_CATEGORIES_INDEX = {
    "student": 0,
    "room": 1,
    "teacher": 2,
    "subject": 3,
    "datetime": 4,
}

def normalize_teacher_name(name: str) -> str:
    if not isinstance(name, str):
        return name

    # spaces normalisation
    s = name.replace("\xa0", " ")
    s = " ".join(s.split())

    result = []
    upper_next = True

    for c in s:
        if c.isalpha():
            if upper_next:
                result.append(c.upper())
                upper_next = False
            else:
                result.append(c.lower())
        else:
            result.append(c)
            upper_next = True

    return "".join(result)



def time_normalizer(date, time, weekday) -> str:


    d = date.date()
    monday = d - timedelta(days=d.weekday())

    dt = datetime.combine(monday, time)
    dt += timedelta(days=weekday)
    return dt.strftime("%Y-%m-%d %H:%M")



def main_normalizer(categories_repartition, active_cells) :
    """
    The main function to normalize the active cells before the files creation.
    Processes the file and calls the normalizers (teacher and time) for each cell.
    Changes the structure of active cells (from [student, date, hour, weekday, room, teacher, subject] to [student, room, formatted_teacher, subject, date & time]).
    :param categories_repartition: The repartition dataframe of all cells from the parsed CSV file
    :param active_cells: The active cells in the dataframe (list of couples representing the coordinates)
    :param subdivide: A boolean whether if the groups of students are subdivided or not
    :return: Modified categories_repartition (in place)
    """
    teacher_index = CATEGORIES_INDEX["teacher"]
    date_index = CATEGORIES_INDEX["date"]
    hour_index = CATEGORIES_INDEX["hour"]
    weekday_index = CATEGORIES_INDEX["weekday"]
    for (row, col) in active_cells:

        cell = categories_repartition.iloc[row, col]
        teacher_name = cell[teacher_index]
        date = cell[date_index]
        hour = cell[hour_index]
        weekday = cell[weekday_index]

        cell[teacher_index] = normalize_teacher_name(teacher_name)
        cell.append(time_normalizer(date, hour, weekday))
        del cell[weekday_index]
        del cell[hour_index]
        del cell[date_index]


def split_num_letter(s):
    match = re.fullmatch(r'(\d+)([a-zA-Z]?)', s)
    if match:
        number = int(match.group(1))
        letter = match.group(2) or None
        return number, letter
    return None


def count_students_per_group(categories_repartition, active_cells) :
    """
    processes every cell to find what letters represent the students for each group
    :param categories_repartition: The repartition dataframe of all cells from the parsed CSV file
    :param active_cells: The active cells in the dataframe (list of couples representing the coordinates)
    :return: a dictionary, where the key is the group and the value is the number of students in that group
    """
    parsed_groups =[]
    students_per_group = {}
    for (row, col) in active_cells:
        cell = categories_repartition.iloc[row, col]
        student = cell[FINAL_CATEGORIES_INDEX["student"]]
        result = split_num_letter(student)
        if result is None :
            raise ValueError(f"Student format not recognised: {student}")
        group, letter = result
        if group not in parsed_groups:
            subgroup = []
            for (row2, col2) in active_cells:
                new_cell = categories_repartition.iloc[row2, col2]
                new_student = new_cell[FINAL_CATEGORIES_INDEX["student"]]
                new_result = split_num_letter(new_student)
                if new_result is None:
                    raise ValueError(f"Student format not recognised: {new_student}")
                new_group, new_letter = new_result
                if new_letter is not None and new_letter.lower() not in subgroup and new_group == group :
                    subgroup.append(new_letter.lower())
            students_per_group[group] = subgroup
            parsed_groups.append(group)
    return students_per_group



def file_creator(categories_repartition, active_cells, subdivide, output_dir=None, date_lang="fr"):
    if output_dir is None:
        output_dir = config.EXPORT_PATH
    students_in_group = count_students_per_group(categories_repartition, active_cells) if subdivide else {}

    student_idx = FINAL_CATEGORIES_INDEX["student"]
    room_idx = FINAL_CATEGORIES_INDEX["room"]
    teacher_idx = FINAL_CATEGORIES_INDEX["teacher"]
    subject_idx = FINAL_CATEGORIES_INDEX["subject"]
    datetime_idx = FINAL_CATEGORIES_INDEX["datetime"]

    groups = {}

    for (row, col) in active_cells:
        cell = categories_repartition.iloc[row, col]

        student = cell[student_idx]
        result = split_num_letter(str(student))
        if result is None:
            raise ValueError(f"Student format not recognised: {student}")
        number, letter = result
        student_key = f"{number}{letter.lower()}" if letter else str(number)

        room = cell[room_idx]
        teacher = cell[teacher_idx]
        subject = cell[subject_idx]
        dt = cell[datetime_idx]

        groups.setdefault(student_key, []).append((dt, room, teacher, subject))


    # propagates the task of the group to every student in the group
    if subdivide:
        for student_key in list(groups.keys()):
            result = split_num_letter(student_key)
            if result is None:
                raise ValueError(f"Student format not recognised: {student_key}")
            number, letter = result

            if letter is None:
                letters = students_in_group.get(number, [])
                if letters:
                    whole_group_tasks = groups.pop(student_key)
                    for l in letters:
                        subgroup_key = f"{number}{l}"
                        groups.setdefault(subgroup_key, []).extend(whole_group_tasks)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    existing_files = []
    header = [
        "TYPE", "CONTENT", "DESCRIPTION", "PRIORITY", "INDENT",
        "AUTHOR", "RESPONSIBLE", "DATE", "DATE_LANG", "TIMEZONE"
    ]

    for student, tasks in groups.items():
        tasks.sort(key=lambda t: t[0])

        rows = []
        for dt, room, teacher, subject in tasks:
            prefix = "d'" if subject[0].lower() in "aeiou" else "de "
            rows.append([
                "task",
                f"Khôlle {prefix}{subject} en {room} avec {teacher}",
                "", "1", "1", "", "",
                dt,
                date_lang, "",
            ])

        filename = output_dir / f"Groupe{student}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

        existing_files.append(str(filename))

    return existing_files

