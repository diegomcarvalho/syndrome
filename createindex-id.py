import glob
import sys
import os


def clean_string(s):
    return s.replace('Cases_on_an_international_conveyance_Japan',
                     'Cases Int Cnv Japan').replace('United_Arab_Emirates',
                                                    'Uni. Arab Emi.').replace('Democratic_Republic_of_the_Congo',
                                                                              'Demo. Rep. Congo').replace('_', ' ')


if len(sys.argv) != 2:
    print(f'{sys.argv[0]}: {sys.argv[0]} <id>')
    sys.exit(0)

try:
    g_id = int(sys.argv[1])
except:
    print(f'id must be an integer [0,8]')
    sys.exit(0)

if g_id < 0 or g_id > 20:
    print(f'processing id must be [0,8]')
    sys.exit(0)

BR_states = ["Sao_Paulo", "Minas_Gerais",  "Rio_de_Janeiro", "Bahia",
             "Parana", "Rio_Grande_do_Sul",  "Pernambuco",  "Ceara",
             "Para",  "Santa_Catarina",  "Maranhao",  "Goias",
             "Amazonas", "Espirito_Santo",  "Paraiba",  "Rio_Grande_do_Norte",
             "Mato_Grosso", "Alagoas", "Piaui", "Distrito_Federal",
             "Mato_Grosso_do_Sul",  "Sergipe",  "Rondonia",  "Tocantins",
             "Acre", "Amapa", "Roraima"]

W_regions = list()
with open('log/processed.log', 'r') as f:
    for line in f.readlines():
        region = line.split(',')
        W_regions.append(region[0].strip())
W_regions.sort()

# Sorry, it O(n), but...
BR_states.sort()
BR_states.insert(0, 'Brasil')
for i in BR_states:
    if i in W_regions:
        W_regions.remove(i)

while 'Brasil' in W_regions:
    W_regions.remove('Brasil')

f = open('index_id_template.html', 'r')

if g_id < 9:
    l = 5 - len(BR_states) % 5
else:
    l = 2 - len(BR_states) % 2

for i in range(l):
    BR_states.append('Brasil')

str_id = 'EDO' if g_id == 6 else 'SOCNET'

for i in range(37):
    line = f.readline()
    print(line.replace('Model', f'{str_id} Model'))

if g_id < 9:
    for i in range(0, len(BR_states), 5):
        name = BR_states[i]
        name = name.replace('_', ' ')
        print(
            f'<tr><td><div class="w3-tiny w3-center">{name}</div><a href="web/{BR_states[i]}.html"><img src="web/svg/{BR_states[i]}-{g_id}.svg" width="150" height="150"/></a></td>')
        name = BR_states[i+1]
        name = name.replace('_', ' ')
        print(
            f'<td><div class="w3-tiny w3-center">{name}</div><a href="web/{BR_states[i+1]}.html"><img src="web/svg/{BR_states[i+1]}-{g_id}.svg" width="150" height="150"/></a></td>')
        name = BR_states[i+2]
        name = name.replace('_', ' ')
        print(
            f'<td><div class="w3-tiny w3-center">{name}</div><a href="web/{BR_states[i+2]}.html"><img src="web/svg/{BR_states[i+2]}-{g_id}.svg" width="150" height="150"/></a></td>')
        name = BR_states[i+3]
        name = name.replace('_', ' ')
        print(
            f'<td><div class="w3-tiny w3-center">{name}</div><a href="web/{BR_states[i+3]}.html"><img src="web/svg/{BR_states[i+3]}-{g_id}.svg" width="150" height="150"/></a></td>')
        name = BR_states[i+4]
        name = name.replace('_', ' ')
        print(
            f'<td><div class="w3-tiny w3-center">{name}</div><a href="web/{BR_states[i+4]}.html"><img src="web/svg/{BR_states[i+4]}-{g_id}.svg" width="150" height="150"/></a></td></tr>')
else:
    for i in range(0, len(BR_states), 2):
        name = BR_states[i]
        name = name.replace('_', ' ')
        print(
            f'<tr><td><div class="w3-tiny w3-center">{name}</div><a href="web/{BR_states[i]}.html"><img src="web/svg/{BR_states[i]}-{g_id}.svg" width="375" height="150"/></a></td>')
        name = BR_states[i+1]
        name = name.replace('_', ' ')
        print(
            f'<td><div class="w3-tiny w3-center">{name}</div><a href="web/{BR_states[i+1]}.html"><img src="web/svg/{BR_states[i+1]}-{g_id}.svg" width="375" height="150"/></a></td></tr>')


if g_id < 9:
    l = 5 - len(W_regions) % 5
    if l != 5:
        for i in range(l):
            W_regions.append('Brazil')
else:
    l = 2 - len(W_regions) % 2
    if l != 2:
        for i in range(l):
            W_regions.append('Brazil')


for i in range(12):
    line = f.readline()
    print(line)

if g_id < 9:
    for i in range(0, len(W_regions), 5):
        name = clean_string(W_regions[i])
        print(
            f'<tr><td><div class="w3-tiny w3-center">{name}</div><a href="web/{W_regions[i]}.html"><img src="web/svg/{W_regions[i]}-{g_id}.svg" width="150" height="150"/></a></td>')
        name = clean_string(W_regions[i+1])
        print(
            f'<td><div class="w3-tiny w3-center">{name}</div><a href="web/{W_regions[i+1]}.html"><img src="web/svg/{W_regions[i+1]}-{g_id}.svg" width="150" height="150"/></a></td>')
        name = clean_string(W_regions[i+2])
        print(
            f'<td><div class="w3-tiny w3-center">{name}</div><a href="web/{W_regions[i+2]}.html"><img src="web/svg/{W_regions[i+2]}-{g_id}.svg" width="150" height="150"/></a></td>')
        name = clean_string(W_regions[i+3])
        print(
            f'<td><div class="w3-tiny w3-center">{name}</div><a href="web/{W_regions[i+3]}.html"><img src="web/svg/{W_regions[i+3]}-{g_id}.svg" width="150" height="150"/></a></td>')
        name = clean_string(W_regions[i+4])
        print(
            f'<td><div class="w3-tiny w3-center">{name}</div><a href="web/{W_regions[i+4]}.html"><img src="web/svg/{W_regions[i+4]}-{g_id}.svg" width="150" height="150"/></a></td></tr>')
else:
    for i in range(0, len(W_regions), 2):
        name = clean_string(W_regions[i])
        print(
            f'<tr><td><div class="w3-tiny w3-center">{name}</div><a href="web/{W_regions[i]}.html"><img src="web/svg/{W_regions[i]}-{g_id}.svg" width="375" height="150"/></a></td>')
        name = clean_string(W_regions[i+1])
        print(f'<td><div class="w3-tiny w3-center">{name}</div><a href="web/{W_regions[i+1]}.html"><img src="web/svg/{W_regions[i+1]}-{g_id}.svg" width="375" height="150"/></a></td></tr>')

for i in f.readlines():
    print(i)

f.close()
