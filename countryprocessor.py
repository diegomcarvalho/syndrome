import numpy as np
import pandas as pd
import os

import ray
import fit

@ray.remote(num_cpus=1)
def process_country(ct, datadict, curdate, paramp, program):

	data = pd.DataFrame(datadict)
	data_consolidated = [ct]
	model_consolidated = list()

	# cases fit
	# Fit on cases per day
	id = 0
	if id in program:
		x = data['eDay'].values
		y = data['cases'].values
		fit.run_model_bell(x, y, ct, id, 'Infected', data_consolidated, model_consolidated, curdate, 'Regression on Cases')

	# Fit on accumulated cases per day
	id = 1
	if id in program:
		x = data['eDay'].values
		y = data['accCases'].values
		fit.run_model_sigmoid(x, y, ct, id, 'Acc Infected', data_consolidated, model_consolidated, curdate, 'Regression on accumulated cases')

	# Draw 7-rolling average
	id = 2
	if id in program:
		x = data['accCases'].values
		rla = data['newcasesroll'].values
		fit.run_rolling_average(x, rla, ct, id, 7, curdate, 'cases')

	# Fit on deaths per day
	id = 3
	if id in program:
		x = data['eDay'].values
		y = data['deaths'].values
		fit.run_model_bell(x, y, ct, id, 'Deaths', data_consolidated, model_consolidated, curdate, 'Regression on deaths')

	# Fit on accumulated cases per day
	id = 4
	if id in program:
		x = data['eDay'].values
		y = data['accDeaths'].values
		fit.run_model_sigmoid(x, y, ct, id, 'Acc deaths', data_consolidated, model_consolidated, curdate, 'Regression on accumulated deaths')

	# Draw 7-rolling average
	id = 5
	if id in program:
		x = data['accDeaths'].values
		rla = data['newdeathsroll'].values
		fit.run_rolling_average(x, rla, ct, id, 7, curdate, 'deaths')

	# Place holder for EDO model
	id = 6
	if id in program:
		x = data['eDay'].values
		y = data['accCases'].values
		mdc = list()
		tag = 'CASES'
		fit.run_edo_model(x, y, ct, id, data, tag, 'Acc Infected', data_consolidated, mdc, curdate, 'SARS-COV-2-EDO-BR Model on cases', paramp)
		model_consolidated.append(mdc[0])
		if mdc[0] is not None:
			paramp.set_param.remote(ct, tag, mdc[0].params)
		
		# Place holder for EDO model
		x = data['eDay'].values
		y = data['accDeaths'].values
		fit.copy_edo_model(x, y, ct, id+1, data, 'DEATHS', 'Acc deaths', data_consolidated, mdc, curdate, 'SARS-COV-2-EDO-BR Model on deaths', paramp)
		model_consolidated.append(mdc[1])

	# Place holder for SOCNET model
	#fit.get_model_socnet(ct, 8, curdate)
	id = 8
	if id in program:
		x = data['eDay'].values
		y = data['accCases'].values
		fit.run_socnet_model(x, y, ct, id, data, 'CASES', 'Acc Infected', data_consolidated, mdc, curdate, 'SARS-COV-2-SOCNET-BR Model on cases')

	id = 9
	if id in program:
		x = data['eDay'].values
		y = data['accCases'].values
		fit.run_data(x, y, ct, id, 'Acc Infected', curdate, 'Current data', txt1='Current Data')

	with open(f'log/{ct}.dat', 'w') as f:
		f.write('process_country')
		for i in data_consolidated:
			f.write(f', {i}')
		f.write('\n')

	rname = ct.replace('_', ' ')
	os.system(f'sed s/COUNTRY_TAG/{ct}/g < template.html | sed "s/COUNTRY_NAME/{rname}/g" > web/{ct}.html')
	os.system(f'cp svg/{ct}*.svg web/svg')
	os.system(f'cp report/{ct}*.html web/report')

	return ct
