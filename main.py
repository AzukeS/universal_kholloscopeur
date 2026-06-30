import sys
from config import *
from parser import *

if not len(PATH) :
    sys.exit("No path provided in config")

print(parse_csv(PATH))