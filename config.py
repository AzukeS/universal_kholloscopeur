# Chemin du fichier à traiter
PATH = "data/kholloscopeA.csv"


# Nom des matières prśentes dans le khôlloscope, sans accents ni majuscules ni casse
MATIERES_ALIASES = {
    "Mathématiques":  ["math", "maths", "mathematique", "mathematiques"],
    "Physique":       ["physique", "pc", "p-c"],
    "SI":             ["si", "sii", "sciences de l'ingenieur", "s.i", "s.i.i"],
    "SVT":            ["svt"],
    "Anglais":        ["anglais", "lv1 anglais", "anglais lv1"],
    "Espagnol":       ["espagnol", "lv2 espagnol", "espagnol lv2"],
    "Français":       ["fr", "francais"],
}


# Nom des mois, qui n'ont pas besoin d'être écrits entièrement dans le csv
# La casse, les accents et les caractères spéciaux ne sont pas non plus ici considérés
FORMAT_ALIASES = {
    1: ["janvier", "january"],
    2: ["fevrier", "february"],
    3: ["mars", "march"],
    4: ["avril", "april"],
    5: ["mai", "may"],
    6: ["juin", "june"],
    # 7: ["juillet", "july"],
    # 8: ["aout", "august"], grandes vacances
    9: ["septembre", "september"],
    10: ["octobre", "october"],
    11: ["novembre", "november"],
    12: ["decembre", "december"]
}

WEEK_DAYS = {
    0: ["lundi"],
    1: ["mardi"],
    2: ["mercredi"],
    3: ["jeudi"],
    4: ["vendredi"],
    5: ["samedi"],
}

# Format des dates, à changer si nécessaire
# Pas besoin de modifier non plus si les dates n'utilisent pas uniquement le format xx/xx
DATE_FORMAT = "dd/mm" # jour / mois

# Combien de caractères sont utilisés pour écrire le mois dans les format du type "12 sept" (au minimum) ?
# En dessous de 2, c'est trop ambigu
WRITTEN_DATE_MIN_CHARACTERS = 3

# Si WRITTEN_DATE_MIN_CHARACTERS = 2, comment sont écrits mars et mai pour éviter les ambiguités ?
WRITTEN_MARCH = "mar"
WRITTEN_MAY = "mai"