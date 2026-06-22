from parser import syntax_parser
from zone import create_zones , Zone


data = syntax_parser("config.txt")
nb_drons = data[0]['nb']
zones = create_zones(data)
print(nb_drons)