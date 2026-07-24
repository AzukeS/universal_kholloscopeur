# Chemin du fichier à traiter
PATH = "data/kholloscopeA.csv"


# Nom des matières prśentes dans le khôlloscope
MATIERES_ALIASES = {
    "Mathématiques":  ["math", "maths", "mathematique", "mathematiques"],
    "Physique":       ["physique", "pc", "p-c"],
    "SI":             ["si", "sii", "sciences de l'ingenieur", "s.i.", "s.i.i.", "s.i", "s.i.i"],
    "SVT":            ["svt"],
    "Anglais":        ["anglais", "lv1 anglais", "anglais lv1"],
    "Espagnol":       ["espagnol", "lv2 espagnol", "espagnol lv2"],
    "Français":       ["fr", "francais"],
}


# Nom des mois, qui n'ont pas besoin d'être écrits entièrement dans le csv
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
    0: ["lu", "lun", "lundi"],
    1: ["ma", "mar", "mardi"],
    2: ["me", "mer", "mercredi"],
    3: ["je", "jeu", "jeudi"],
    4: ["ve", "ven", "vendredi"],
    5: ["sa", "sam", "samedi"], # j'espère sincèrement que personne n'a khôlle le samedi mais on sait jamais...
}

# Format des dates, à changer si nécessaire
# Pas besoin de modifier non plus si les dates utilisent un format textuel (e.g 12-septembre)
DATE_FORMAT = "dd/mm" # jour / mois

# Combien de caractères sont utilisés pour écrire le mois dans les formats du type "12 sept" (au minimum) ?
# En dessous de 2, c'est trop ambigu
WRITTEN_DATE_MIN_CHARACTERS = 3

# Si WRITTEN_DATE_MIN_CHARACTERS == 2, comment sont écrits mars et mai pour éviter les ambiguités ?
WRITTEN_MARCH = "mar"
WRITTEN_MAY = "mai"


# Nom des salles particulières (i.e. d'un format autre que lettre + chiffres ou juste chiffres)
# Toujours pas besoin de mettre les accents / caractères spéciaux ni majuscules
SPECIAL_ROOMS = [
    "labo s.i."
]

# Ce qui précède le nom d'un professeur dans le khôlloscope (par exemple "Mme" pour "Mme. Dupont")
TEACHER_TITLES = [
    "Mme",
    "Mrs",
    "Mr",
    "M",
]

# Nom de la catégorie pour les salles, professeurs, matière (e.g. "Salle") (toujours pas besoin de majuscules / caractères spéciaux)
ROOM_LABELS = ["salle"]
TEACHER_LABELS = ["prof", "professeur", "professeurs", "interrogateur", "enseignant", "colleur", "kholleur",]
SUBJECTS_LABELS = ["matiere"]
