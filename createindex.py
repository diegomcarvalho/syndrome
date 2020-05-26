import glob
import sys
import os

BR_states = ["Sao_Paulo", "Minas_Gerais",  "Rio_de_Janeiro", "Bahia",
         "Parana", "Rio_Grande_do_Sul",  "Pernambuco",  "Ceara",
         "Para",  "Santa_Catarina",  "Maranhao",  "Goias",
         "Amazonas", "Espirito_Santo",  "Paraiba",  "Rio_Grande_do_Norte",
         "Mato_Grosso", "Alagoas","Piaui", "Distrito_Federal",
         "Mato_Grosso_do_Sul",  "Sergipe",  "Rondonia",  "Tocantins",
         "Acre", "Amapa", "Roraima"]

W_regions =list()
with open('log/processed.log', 'r') as f:
	for line in f.readlines():
		region = line.split(',')
		W_regions.append(region[0].strip())
W_regions.sort()

# Sorry, it O(n), but...
BR_states.sort()
BR_states.insert(0,'Brasil')
for i in BR_states:
	if i in W_regions:
		W_regions.remove(i)

while 'Brasil' in W_regions:
	W_regions.remove('Brasil')

f = open('index_template.html', 'r')

l = 5 - len(BR_states) % 5
for i in range(l):
	BR_states.append('Brasil')

for i in range(27):
	line = f.readline()
	print(line)

for i in range(0, len(BR_states), 5):
	name = BR_states[i]
	name = name.replace('_',' ')
	print(f'<tr><td><div><a href="web/{BR_states[i]}.html">{name}</a></div></td>')
	name = BR_states[i+1]
	name = name.replace('_',' ')
	print(f'<td><div><a href="web/{BR_states[i+1]}.html">{name}</a></div></td>')
	name = BR_states[i+2]
	name = name.replace('_',' ')
	print(f'<td><div><a href="web/{BR_states[i+2]}.html">{name}</a></div></td>')
	name = BR_states[i+3]
	name = name.replace('_',' ')
	print(f'<td><div><a href="web/{BR_states[i+3]}.html">{name}</a></div></td>')
	name = BR_states[i+4]
	name = name.replace('_',' ')
	print(f'<td><div><a href="web/{BR_states[i+4]}.html">{name}</a></div></td></tr>')


l = 5 - len(W_regions) % 5
if l != 5:
	for i in range(l):
		W_regions.append('Brazil')

for i in range(11):
	line = f.readline()
	print(line)

for i in range(0, len(W_regions), 5):
	name = W_regions[i]
	name = name.replace('_', ' ')
	print(f'<tr><td><div><a href="web/{W_regions[i]}.html">{name}</a></div></td>')
	name = W_regions[i+1]
	name = name.replace('_', ' ')
	print(f'<td><div><a href="web/{W_regions[i+1]}.html">{name}</a></div></td>')
	name = W_regions[i+2]
	name = name.replace('_', ' ')
	print(f'<td><div><a href="web/{W_regions[i+2]}.html">{name}</a></div></td>')
	name = W_regions[i+3]
	name = name.replace('_', ' ')
	print(f'<td><div><a href="web/{W_regions[i+3]}.html">{name}</a></div></td>')
	name = W_regions[i+4]
	name = name.replace('_', ' ')
	print(f'<td><div><a href="web/{W_regions[i+4]}.html">{name}</a></div></td></tr>')


for i in f.readlines():
	print(i)

f.close()
