import unicodedata
from config import MATIERES_ALIASES, FORMAT_ALIASES

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


def match_matiere(x):
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
