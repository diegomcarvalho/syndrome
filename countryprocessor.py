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
	g_id = 0
	if g_id in program:
		x = data['eDay'].values
		y = data['cases'].values
		fit.run_model_bell(x, y, ct, g_id, 'Infected', data_consolidated, model_consolidated, curdate, 'Regression on Cases')

	# Fit on accumulated cases per day
	g_id = 1
	if g_id in program:
		x = data['eDay'].values
		y = data['accCases'].values
		fit.run_model_sigmoid(x, y, ct, g_id, 'Acc Infected', data_consolidated, model_consolidated, curdate, 'Regression on accumulated cases')

	# Draw 7-rolling average
	g_id = 2
	if g_id in program:
		x = data['accCases'].values
		rla = data['newcasesroll'].values
		fit.run_rolling_average(x, rla, ct, g_id, 7, curdate, 'cases')

	# Fit on deaths per day
	g_id = 3
	if g_id in program:
		x = data['eDay'].values
		y = data['deaths'].values
		fit.run_model_bell(x, y, ct, g_id, 'Deaths', data_consolidated, model_consolidated, curdate, 'Regression on deaths')

	# Fit on accumulated cases per day
	g_id = 4
	if g_id in program:
		x = data['eDay'].values
		y = data['accDeaths'].values
		fit.run_model_sigmoid(x, y, ct, g_id, 'Acc deaths', data_consolidated, model_consolidated, curdate, 'Regression on accumulated deaths')

	# Draw 7-rolling average
	g_id = 5
	if g_id in program:
		x = data['accDeaths'].values
		rla = data['newdeathsroll'].values
		fit.run_rolling_average(x, rla, ct, g_id, 7, curdate, 'deaths')

	# Place holder for EDO model
	g_id = 6
	if g_id in program:
		mdc = list()
		tag = 'accCases'
		fit.run_edo_model(ct, g_id, data, tag, 'Acc Infected', data_consolidated, mdc, curdate, 'SIMDRQME Model on cases', paramp)
		model_consolidated.append(mdc[0])
		if mdc[0] is not None:
			paramp.set_param.remote(ct, tag, mdc[0].params)
		
		# Place holder for EDO model
		fit.copy_edo_model(ct, g_id+1, data, 'accDeaths', 'Acc deaths', data_consolidated, mdc, curdate, 'SIMDRQME Model on deaths', paramp)
		model_consolidated.append(mdc[1])

	# Place holder for SOCNET model
	#fit.get_model_socnet(ct, 8, curdate)
	g_id = 8
	if g_id in program:
		x = data['eDay'].values
		y = data['accCases'].values
		fit.run_socnet_model(x, y, ct, g_id, data, 'accCases', 'Acc Infected', data_consolidated, mdc, curdate, 'SARS-COV-2-SOCNET-BR Model on cases')

	g_id = 9
	if g_id in program:
		x = data['eDay'].values
		y = data['accCases'].values
		fit.run_data(x, y, ct, g_id, 'Acc Infected', curdate, 'Current data', txt1='Current Data')

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
