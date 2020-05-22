import pandas as pd

def split_field(s):
	s = s.strip()
	s1, s2 = s.split(':')
	s1 = s1.replace(' ', '')
	s2 = s2.replace(' ', '')
	return s1, s2

def read_config(cnfid):
	ret =  dict()
	file_general = f'config/{cnfid}'
	ret['FILE_GENERAL'] = file_general

	with open(file_general, 'r') as f:
		for i in f.readlines():
			tk, val = split_field(i)
			ret[tk] = val

	lr = list()
	with open(ret['REGION_FILE'], 'r') as f:
		for i in f.readlines():
			lr.append(i.strip())

	ret['REGIONS'] = lr

	return ret
