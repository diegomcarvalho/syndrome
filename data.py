import numpy as np
import pandas as pd
import datetime as dt
import os

pop = {"SP": 45919049, "MG": 21168791, "RJ": 17264943, "BA": 14873064,
       "PR": 11433957, "RS": 11377239, "PE": 9557071, "CE": 9132078,
       "PA": 8602865, "SC": 7164788, "MA": 7075181, "GO": 7018354,
       "AM": 4144597, "ES": 4018650, "PB": 4018127, "RN": 3506853,
       "MT": 3484466, "AL": 3337357, "PI": 3273227, "DF": 3015268,
       "MS": 2778986, "SE": 2298696, "RO": 1777225, "TO": 1572866,
       "AC": 881935, "AP": 845731, "RR": 605761}

names = {"SP": "Sao_Paulo", "MG": "Minas_Gerais", "RJ": "Rio_de_Janeiro", "BA": "Bahia",
         "PR": "Parana", "RS": "Rio_Grande_do_Sul", "PE": "Pernambuco", "CE": "Ceara",
         "PA": "Para", "SC": "Santa_Catarina", "MA": "Maranhao", "GO": "Goias",
         "AM": "Amazonas", "ES": "Espirito_Santo", "PB": "Paraiba", "RN": "Rio_Grande_do_Norte",
         "MT": "Mato_Grosso", "AL": "Alagoas", "PI": "Piaui", "DF": "Distrito_Federal",
         "MS": "Mato_Grosso_do_Sul", "SE": "Sergipe", "RO": "Rondonia", "TO": "Tocantins",
         "AC": "Acre", "AP": "Amapa", "RR": "Roraima"}

def brasilian_regions():
	l = list(names.values())
	l.append('Brasil')

	return l

def process_CDCEU(database, fetchdata=True):

	if fetchdata:
		df = pd.read_csv('https://opendata.ecdc.europa.eu/covid19/casedistribution/csv')
		df.to_csv('data/ECDC.csv')
	else:
		df = pd.read_csv('data/ECDC.csv')

	for ct in df.countriesAndTerritories.unique():
		country_name = ct.replace('ç', 'c')

		try:
			# Select Country and sort by year-month-day
			cur = pd.DataFrame(df[df['countriesAndTerritories'] == ct])
			cur = cur.sort_values(['year', 'month', 'day'])

			# Create two new columns: accCases and accDeaths
			cur['accCases'] = cur.cases.cumsum()
			cur['accDeaths'] = cur.deaths.cumsum()

			# Drop all with accumulated sum == 0, since they got before the first case
			cur = cur[cur['accCases'] != 0]

			curdate = f"{cur['year'].iloc[-1]:04}-{cur['month'].iloc[-1]:02}-{cur['day'].iloc[-1]:02}"
			pop = int(cur['popData2018'].iloc[-1])
			accases = int(cur['accCases'].iloc[-1])
		except:
			continue

		# Check if there is any data...
		if len(cur) <= 20 or cur['cases'].sum() < 400:
			continue

		# Reset the index, so index + 1 is the epidemilogical day
		cur = cur.reset_index()
		cur = cur.drop('index', axis=1)
		cur['eDay'] = cur.index + 1

		# Calculate the rolling sum
		cur['newcasesroll'] = cur['cases'].rolling(7).sum()
		cur['newdeathsroll'] = cur['deaths'].rolling(7).sum()

		database[country_name] = { 'DATE': curdate, 'DATA': cur.to_dict(), 'ACCASES': accases, 'POPULATION': pop }
	return


def process_Brazil_MS(df, database):
	state = df[(df['regiao'] == 'Brasil') & (df['populacaoTCU2019'] == 210147125)]
	state = state.sort_values(['data'])
	data = list(np.diff(state.casosAcumulado, prepend=[0]))
	cumdata = list(state.casosAcumulado.values)
	death = list(np.diff(state.obitosAcumulado, prepend=[0]))
	cumdeath = list(state.obitosAcumulado.values)
	population = [210147125 for _ in range(len(data))]
	dates = state.data

	size = len(cumdata)
	day = np.arange(size) + 1
	values = {"data": dates, "eDay": day, "cases": data,
           "accCases": cumdata, "popData2018": population, "deaths": death, "accDeaths": cumdeath}

	cur = pd.DataFrame(values)

	# Drop all with accumulated sum == 0, since they got before the first case
	cur = cur[cur['accCases'] != 0]

	curdate = f"{cur['data'].iloc[-1]}".replace('00:00:00', '')
	popdata = int(cur['popData2018'].iloc[-1])
	accases = int(cur['accCases'].iloc[-1])

	# Reset the index, so index + 1 is the epidemilogical day
	cur = cur.reset_index()
	cur = cur.drop('index', axis=1)
	cur['eDay'] = cur.index + 1

	# Calculate the rolling sum
	cur['newcasesroll'] = cur['cases'].rolling(7).sum()
	cur['newdeathsroll'] = cur['deaths'].rolling(7).sum()

	database['Brasil'] = { 'DATE': curdate, 'DATA': cur.to_dict(), 'ACCASES': accases, 'POPULATION': popdata }

	return

def process_MS(database, fetchdata=True):

	month = {'01': 'jan', '02': 'fev', '03': 'mar',
	         '04': 'abr', '05': 'mai', '06': 'jun',
		     '07': 'jul', '08': 'ago', '09': 'set',
			 '10': 'out', '11': 'nov', '12': 'dec'}

	df = None
	today = dt.date.today()
	for backday in range(5):
		day = today - dt.timedelta(days=backday)
		syear =day.strftime('%Y')
		smonth =day.strftime('%m')
		sday =day.strftime('%d')
		filename = f'data/DT_PAINEL_COVIDBR_{syear}{smonth}{sday}.xlsx'
		if  os.path.exists(filename):
			df = pd.read_excel(filename)
			break
		filename = f'data/HIST_PAINEL_COVIDBR_{sday}{month[smonth]}{syear}.xlsx'
		if  os.path.exists(filename):
			df = pd.read_excel(filename)
			break

	if df is None:
		df = pd.read_csv('data/MS.csv')

	df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')

	process_Brazil_MS(df, database)

	for ct in pop.keys():
		state = df[ (df['estado'] == ct) & (df['populacaoTCU2019'] == pop[ct]) ]
		state = state.sort_values(['data'])
		data = list(np.diff(state.casosAcumulado, prepend=[0]))
		cumdata = list(state.casosAcumulado.values)
		death = list(np.diff(state.obitosAcumulado, prepend=[0]))
		cumdeath = list(state.obitosAcumulado.values)
		population = [pop[ct] for _ in range(len(data))]
		dates = state.data

		size = len(cumdata)
		day = np.arange(size) + 1
		values = {"data": dates, "eDay": day, "cases": data,
			"accCases": cumdata, "popData2018": population, "deaths": death, "accDeaths": cumdeath}

		cur = pd.DataFrame(values)

		# Drop all with accumulated sum == 0, since they got before the first case
		cur = cur[cur['accCases'] != 0]

		curdate = f"{cur['data'].iloc[-1]}".replace('00:00:00', '')
		popdata = int(cur['popData2018'].iloc[-1])
		accases = int(cur['accCases'].iloc[-1])

		# Check if there is any data...
		if len(cur) <= 5 or cur['cases'].sum() < 100:
			#logging.info(f'Cannot fit {ct} due to lack of cases')
			continue

		# Reset the index, so index + 1 is the epidemilogical day
		cur = cur.reset_index()
		cur = cur.drop('index', axis=1)
		cur['eDay'] = cur.index + 1

		# Calculate the rolling sum
		cur['newcasesroll'] = cur['cases'].rolling(7).sum()
		cur['newdeathsroll'] = cur['deaths'].rolling(7).sum()

		database[names[ct]] = { 'DATE': curdate, 'DATA': cur.to_dict(), 'ACCASES': accases, 'POPULATION': popdata }
	return

def build_database(fetchdata=True):
	global_database = dict()

	process_MS(global_database, fetchdata)
	process_CDCEU(global_database, fetchdata)

	return global_database


