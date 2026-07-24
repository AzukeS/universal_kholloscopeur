from datetime import time, datetime, timedelta
from utils import CATEGORIES_INDEX

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





def file_creator(categories_repartition, active_cells, subdivide) :
    """
    The main function to create the files
    :param categories_repartition: The repartition dataframe of all cells from the parsed CSV file
    :param active_cells: The active cells in the dataframe (list of couples representing the coordinates)
    :param subdivide: A boolean whether if the groups of students are subdivided or not
    :return: In place, created files
    """
