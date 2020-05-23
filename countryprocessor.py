import numpy as np
import pandas as pd
import os

import ray
import fit

@ray.remote(num_cpus=0.9)
def process_country(ct, datadict, curdate, paramp):

	data = pd.DataFrame(datadict)
	data_consolidated = [ct]
	model_consolidated = list()

	# cases fit
	# Fit on cases per day
	x = data['eDay'].values
	y = data['cases'].values
	fit.run_model_bell(x, y, ct, 0, 'Infected', data_consolidated, model_consolidated, curdate, 'Regression on Cases')

	# Fit on accumulated cases per day
	x = data['eDay'].values
	y = data['accCases'].values
	fit.run_model_sigmoid(x, y, ct, 1, 'Acc Infected', data_consolidated, model_consolidated, curdate, 'Regression on accumulated cases')

	# Draw 7-rolling average
	x = data['accCases'].values
	rla = data['newcasesroll'].values
	fit.run_rolling_average(x, rla, ct, 2, 7, curdate, 'cases')

	# Fit on deaths per day
	x = data['eDay'].values
	y = data['deaths'].values
	fit.run_model_bell(x, y, ct, 3, 'Deaths', data_consolidated, model_consolidated, curdate, 'Regression on deaths')

	# Fit on accumulated cases per day
	x = data['eDay'].values
	y = data['accDeaths'].values
	fit.run_model_sigmoid(x, y, ct, 4, 'Acc deaths', data_consolidated, model_consolidated, curdate, 'Regression on accumulated deaths')

	# Draw 7-rolling average
	x = data['accDeaths'].values
	rla = data['newdeathsroll'].values
	fit.run_rolling_average(x, rla, ct, 5, 7, curdate, 'deaths')

	# Place holder for EDO model
	x = data['eDay'].values
	y = data['accCases'].values
	mdc = list()
	fit.run_edo_model(x, y, ct, 6, data, 'CASES', 'Acc Infected', data_consolidated, mdc, curdate, 'SARS-COV-2-EDO-BR Model on cases')
	if len(mdc) == 1:
		paramp.set_param.remote(ct,mdc[0])
		model_consolidated.append(mdc[0])
		
	# Place holder for EDO model
	x = data['eDay'].values
	y = data['accDeaths'].values
	fit.run_edo_model(x, y, ct, 7, data, 'DEATHS', 'Acc deaths', data_consolidated, model_consolidated, curdate, 'SARS-COV-2-EDO-BR Model on deaths')

	# Place holder for SOCNET model
	#fit.get_model_socnet(ct, 8, curdate)
	x = data['eDay'].values
	y = data['accCases'].values
	fit.run_socnet_model(x, y, ct, 8, data, 'CASES', 'Acc Infected', data_consolidated, mdc, curdate, 'SARS-COV-2-SOCNET-BR Model on cases')

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
