import itertools
import math as m
import os

import lmfit as lm
import numba
import numpy as np
import pandas as pd
import svg
import ray
from lmfit.models import (BreitWignerModel, DampedOscillatorModel,
						  GaussianModel, LinearModel, LognormalModel,
						  LorentzianModel, MoffatModel, Pearson7Model,
						  PseudoVoigtModel, SkewedGaussianModel,
						  SkewedVoigtModel, SplitLorentzianModel, StepModel,
						  StudentsTModel, VoigtModel)

import edocovid as edo
from htmltemplate import param_page, param_page1
from svg import dump_svg, dump_svg2D, dump_svg_ph


def dump_xy_dat(filename, x, y):
	with open(filename, 'w') as f:
		for i, j in itertools.zip_longest(x, y, fillvalue='nan'):
			f.write(f'{i}, {j}\n')
	return

def dump_xyz_dat(filename, x, y, z):
	with open(filename, 'w') as f:
		for i, j, k in itertools.zip_longest(x, y, z, fillvalue='nan'):
			f.write(f'{i}, {j}, {k}\n')


def dump_report(filename, result, x, y, forecast_size, fsvg, model, ct, ylabel):
	rname = ct.replace('_', ' ')
	table_info = f'<tr><td>Success status</td><td>{result.success}</td></tr>'
	table_info += f'<tr><td>Abort status</td><td>{result.aborted}</td></tr>'
	table_info += f'<tr><td>Fit message</td><td>{result.message}</td></tr>'
	table_stat = '<tr> <td>' + result._repr_html_() + '</td></tr>'
	table_obs = f'<tr><th>Days from the first infected</th><th>{ylabel}</th><th>Model {ylabel}</th></tr>'

	if result != None:
		nx = np.arange(x[-1] + 7)
		try:
			forecast = model.eval(result.params,x=nx)
			for i, j, k in itertools.zip_longest(nx, y, forecast, fillvalue='nan'):
				table_obs += f'<tr><td>{i}</td><td>{j}</td><td>{k:.0f}</td></tr>'
		except Exception as e:
			print(f'dump_report: {ct} {model} {e}, generating report without forecast')
			for i, j in itertools.zip_longest(x, y, fillvalue='nan'):
				table_obs += f'<tr><td>{i}</td><td>{j}</td><td>{e}</td></tr>'

	with open(filename, 'w') as f:
		f.write(param_page(rname, table_info, table_stat, table_obs,fsvg))
	return

def fit_bell_shape(x, y, mod):
	mod = mod()
	pars = mod.guess(y, x=x)
	result = mod.fit(y, pars, x=x)
	return result, mod

def gompertz(x, asymptote, displacement, step_center):
	transform = 1.0 + x
	c = m.log(m.log(2.0) / displacement) / step_center
	return asymptote * np.exp(- displacement * np.exp(-c * transform))

def find_fit_sigmoid(x, y):
	model_gompertz = lm.models.Model(gompertz)
	params_gompertz = lm.Parameters()
	params_gompertz.add('asymptote', value=1E-3, min=1E-8)
	params_gompertz.add('displacement', value=1E-3, min=1E-8)
	params_gompertz.add('step_center', value=1E-3, min=1E-8)

	result_gompertz = model_gompertz.fit(y, params_gompertz, x=x)

	step_mod = StepModel(form='erf', prefix='step_')
	line_mod = LinearModel(prefix='line_')

	params_stln = line_mod.make_params(intercept=y.min(), slope=0)
	params_stln += step_mod.guess(y, x=x, center=90)

	model_stln = step_mod + line_mod
	result_stln = model_stln.fit(y, params_stln, x=x)

	ret_result = None
	ret_model = None

	if result_stln.chisqr < result_gompertz.chisqr:
		ret_result = result_stln
		ret_model = model_stln
	else:
		ret_result = result_gompertz
		ret_model = model_gompertz

	return ret_result, ret_model

def find_fit_bell(x, y, ct, log=False):

	ret_result = None
	ret_model = None
	current_min_chisqr = np.inf

	old_list = [DampedOscillatorModel, MoffatModel, BreitWignerModel]

	for m in [GaussianModel, LorentzianModel, VoigtModel, PseudoVoigtModel,  Pearson7Model, StudentsTModel, LognormalModel,  SkewedGaussianModel, SkewedVoigtModel, SplitLorentzianModel]:
		#if log:
			#loggingg.info(f'find_fit_bell: {mod}')

		result, model = fit_bell_shape(x, y, m)

		if result.success == False or result.chisqr > current_min_chisqr:
			continue

		ret_result = result
		ret_model = model
		current_min_chisqr = ret_result.chisqr

	#if model_fit == None:
		#loggingg.info(f'find_fit_bell: cannot fit for {ct}')

	return ret_result, ret_model

def run_model_bell(x, y, ct, g_id, ylabel, data_consolidated, model_consolidated, curdate, text):
	rname = ct.replace('_', ' ')
	fdata = f'gpdata/dat/{ct}-{g_id}.dat'
	fgplot = f'gpdata/{ct}-{g_id}.gp'
	fsvg = f'svg/{ct}-{g_id}.svg'
	freport = f'report/{ct}-{g_id}.html'

	result, model = find_fit_bell(x, y, ct)

	if result == None:
		data_consolidated.append('n.a.')
		data_consolidated.append('n.a.')
		dump_xy_dat(fdata,x,y)
		dump_svg(fgplot, fsvg,
					f'{text} for {rname} on {curdate}',
					'Days from the first infected',
					f'{ylabel}', f'gpdata/dat/{ct}-{g_id}.dat', 2, f"{rname} data",
					opt='colorsequence podo',
					txt1='NO FIT AVAILABLE FOR THE CURRENT DATA', point=True)
		#loggingg.info(f'run_model_bell: cannot fit deaths for {ct}')
	else:
		center = int(round(result.params['center'].value))
		chisqr = result.chisqr

		data_consolidated.append(center)
		data_consolidated.append(chisqr)
		model_consolidated.append(result)

		dump_xyz_dat(fdata,x,y,result.best_fit)

		dump_svg2D(fgplot, fsvg,
					f'{text} for {rname} on {curdate}',
					'Days from the first infected',
					f'{ylabel}',
					fdata, 2, 3, f"{rname} data",
					f'{text}',
					opt='yrange [0<*:]',
					txt1=f'Mid = {center} days',
					txt2=f'𝛘² = {chisqr:9.2}')
	dump_report(freport,result,x,y,7,fsvg,model,ct,ylabel)
	return

def run_model_sigmoid(x, y, ct, g_id, ylabel, data_consolidated, model_consolidated, curdate, text):
	rname = ct.replace('_', ' ')
	fdata = f'gpdata/dat/{ct}-{g_id}.dat'
	fgplot = f'gpdata/{ct}-{g_id}.gp'
	fsvg = f'svg/{ct}-{g_id}.svg'
	freport = f'report/{ct}-{g_id}.html'

	result, model = find_fit_sigmoid(x, y)

	if result.success == False:
		data_consolidated.append('n.a.')
		data_consolidated.append('n.a.')

		dump_xy_dat(fdata,x,y)
		dump_svg(fgplot, fsvg,
					f'{text} for {rname} on {curdate}',
					'Days from the first infected',
					f'{ylabel}', fdata, 2, f"{rname} data",
					opt='colorsequence podo',
					txt1='NO FIT AVAILABLE FOR THE CURRENT DATA', point=True)
		#loggingg.info(f'run_model_sigmoid: cannot fit sigmoid for {ct}')
	else:
		chisqr = result.chisqr
		center = int(round(result.params['step_center'].value))

		data_consolidated.append(center)
		data_consolidated.append(chisqr)
		model_consolidated.append(result)

		dump_xyz_dat(fdata,x,y,result.best_fit)
		dump_svg2D(fgplot, fsvg,
					f'{text} for {rname} on {curdate}',
					'Days from the first infected',
					f'{ylabel}',
					fdata, 2, 3,
					f"{rname} data",
					f'{text}',
					opt='yrange [0<*:]',
					txt1=f'Mid = {center} days',
					txt2=f'𝛘² = {chisqr:9.2}')

	dump_report(freport,result,x,y,7,fsvg,model,ct,ylabel)
	return

def get_edo_config(ct, cur, tag, paramp):
	print(f"{ct} - {tag}")
	if tag == 'accCases':
		x = list(cur['eDay'])
		y = list(cur[tag])
		days = len(x)
		residual = edo.residual_edo_D
		ffunct = edo.eval_edo_D
	elif tag == 'perCases':
		x = list(cur['eDay'])
		y = list(cur['accCases']/cur['popData2019'])
		days = len(x)
		residual = edo.residual_edo_D
		ffunct = edo.eval_edo_D
	elif tag == 'accCombined':
		x = np.append(cur['eDay'],cur['eDay'])
		y = np.append(cur['accCases'], cur['accDeaths'])
		days = len(x)//2
		residual = edo.residual_edo_combined
		ffunct = edo.eval_edo_D
	elif tag == 'accDeaths':
		x = list(cur['eDay'])
		y = list(cur[tag])
		days = len(x)
		residual = edo.residual_edo_M
		ffunct = edo.eval_edo_M

	if paramp is not None:
		future = paramp.get_param.remote(ct, tag)

	pop = int(cur['popData2019'].iloc[-1])
	a = 1.2
	i = 1.8
	gammaD = 0.14
	death_rate = cur['accDeaths'].iloc[-1] / cur['accCases'].iloc[-1]  # 0.035
	dD = gammaD * death_rate / (1 - death_rate)

	if paramp is not None:
		params = ray.get(future)
	else:
		params = lm.Parameters()

	if len(params.items()) == 0:
		params = lm.Parameters()
		params.add('beta',     value=0.000012,  min=0.000,   max=1.00, vary=True)
		params.add('rho',      value=0.550,     min=0.550,   max=0.60, vary=True)
		params.add('p',        value=0.001,     min=0.001,   max=1.00, vary=True)
		params.add('epsilonA', value=0.000,     min=0.0100,  max=4.00, vary=True)
		params.add('epsilonI', value=0.200,     min=0.0100,  max=4.00, vary=True)
		params.add('cD',       value=1.400,     min=1.100,   max=1.70, vary=True)
		params.add('gammaI',   value=1/22,      min=1/42,    max=1/14, vary=True)
		params.add('gammaD',   value=1/22,      min=1/42,    max=1/14, vary=True)
		params.add('delta',    value=0.0001,    min=0.0000,  max=1.00, vary=True)

		params.add('theta',   value=8/19,     vary=False)
		params.add('sigma',   value=1/5.1,    vary=False)
		params.add('lambda0', value=1/len(y), vary=False)
		params.add('gammaA',  value=1/14,     vary=False)

		params.add('dD', expr=f'gammaD*{death_rate}/(1-{death_rate})')
		params.add('dI', expr='cD*dD')

		params.add('pop', value=pop, vary=False)

		params.add('N0', value=1.25*y[-1], min=0, max=pop,            vary=True)
		params.add('S0', value=0,          min=0, max=0.5*pop - 2 * y[0], vary=True)

		params.add('R0', value=0,    vary=False)
		params.add('E0', value=0,    vary=False)
		params.add('A0', value=0,    vary=False)
		params.add('I0', value=y[0], vary=False)
		params.add('D0', value=y[0], vary=False)
		params.add('M0', value=0,    vary=False)
		params.add('Q0', expr="N0-S0-E0-A0-I0-D0-R0-M0", min=0.0)

		params.add('pop', value=pop,  vary=False)
		params.add('day', value=days, vary=False)

	else:
		params.add('theta',   value=8/19,     vary=False)
		params.add('sigma',   value=1/5.1,    vary=False)
		params.add('lambda0', value=1/len(y), vary=False)
		params.add('gammaA',  value=1/14,     vary=False)

		params.add('dD', expr=f'gammaD*{death_rate}/(1-{death_rate})')
		params.add('dI', expr='cD*dD')

		params.add('pop', value=pop, vary=False)

		params.add('N0', value=1.25*y[-1], min=0, max=pop,            vary=True)
		params.add('S0', value=0,          min=0, max=0.5*pop - 2 * y[0], vary=True)

		params.add('R0', value=0,    vary=False)
		params.add('E0', value=0,    vary=False)
		params.add('A0', value=0,    vary=False)
		params.add('I0', value=y[0], vary=False)
		params.add('D0', value=y[0], vary=False)
		params.add('M0', value=0,    vary=False)
		params.add('Q0', expr="N0-S0-E0-A0-I0-D0-R0-M0", min=0.0)

		params.add('pop', value=pop,  vary=False)
		params.add('day', value=days, vary=False)

	return x, y, params, residual, ffunct

def fit_edo_shape(ct, cur, tag, paramp=None, forecast_days=14):

	x, y, params, func, ffunc = get_edo_config(ct, cur, tag, paramp)

	minner = lm.Minimizer(func, params, fcn_args=(y, params))
	result = minner.minimize(max_nfev=150000, method='powell')

	forecast = None if result.success == False else ffunc(result.params, forecast_days)

	return x, y, result, forecast

def copy_edo_shape(ct, cur, tag1, model, paramp=None, forecast_days=14):

	tag2 = 'accDeaths' if tag1 == 'accCases' else 'accCases'
	x, y, params1, func1, ffunc1 = get_edo_config(ct, cur, tag1, paramp)
	x, y, params3, func2, ffunc2 = get_edo_config(ct, cur, tag2, paramp)

	if model is None:
		params2 = params3
	else:
		params2 = model.params

	minner = lm.Minimizer(func1, params2, fcn_args=(y, params2))
	result = minner.minimize(max_nfev=35000, ftol=1.49012e-09, xtol=1.49012e-09)

	forecast = None if result.success == False else ffunc1(result.params, forecast_days)

	return x, y, result, forecast


def copy_edo_model(ct, g_id, cur, tag, ylabel, data_consolidated, model_consolidated, curdate, text, paramp=None, forecast_days=14):
	rname = ct.replace('_', ' ')
	fdata = f'gpdata/dat/{ct}-{g_id}.dat'
	fgplot = f'gpdata/{ct}-{g_id}.gp'
	fsvg = f'svg/{ct}-{g_id}.svg'
	freport = f'report/{ct}-{g_id}.html'

	x, y, model, forecast = copy_edo_shape(ct, cur, tag, model_consolidated[0], paramp, forecast_days)

	if model.success == False:
		data_consolidated.append('n.a.')
		model_consolidated.append(None)

		dump_xy_dat(fdata,x,y)
		dump_svg(fgplot, fsvg,
					f'{text} for {rname} on {curdate}',
					'Days from the first infected',
					f'{ylabel}', fdata, 2, f"{rname} data",
					opt='colorsequence podo',
					txt1='NO FIT AVAILABLE FOR THE CURRENT DATA', point=True)
	else:
		chisqr = model.chisqr
		data_consolidated.append(chisqr)
		model_consolidated.append(model)
		nx = x if forecast is None else np.arange(len(forecast))
		dump_xyz_dat(fdata, nx, y, forecast)
		dump_svg2D(fgplot, fsvg,
					f'{text} for {rname} on {curdate}',
					'Days from the first infected',
					f'{ylabel}',
					fdata, 2, 3,
					f"{rname} data",
					f'{text}',
					opt='yrange [0<*:]',
					txt1=f'EDO',
					txt2=f'𝛘² = {chisqr:9.2}')

	if model != None:		
		with open(freport, 'w') as f:
			table_info = f'<tr><td>Success status</td><td>{model.success}</td></tr>'
			table_info += f'<tr><td>Abort status</td><td>{model.aborted}</td></tr>'
			table_info += f'<tr><td>Fit message</td><td>{model.message}</td></tr>'
			table_stat = '<tr> <td>' + model._repr_html_() + '</td></tr>'
			table_obs = f'<tr><th>Days from the first infected</th><th>{ylabel}</th><th>Model {ylabel}</th></tr>'
			if forecast != None:
				for i, j, k in itertools.zip_longest(nx, y, forecast, fillvalue='nan'):
					table_obs += f'<tr><td>{i}</td><td>{j}</td><td>{k:.0f}</td></tr>'
			else:
				for i, j in itertools.zip_longest(x, y, fillvalue='nan'):
					table_obs += f'<tr><td>{i}</td><td>{j}</td><td>n.a.</td></tr>'
			f.write(param_page(rname, table_info, table_stat, table_obs,fsvg))
	return

def run_edo_model(ct, g_id, cur, tag, ylabel, data_consolidated, model_consolidated, curdate, text, paramp=None, forecast_days=14):
	rname = ct.replace('_', ' ')
	fdata = f'gpdata/dat/{ct}-{g_id}.dat'
	fdatc = f'gpdata/dat/{ct}-{g_id+10}.dat'
	fgplot = f'gpdata/{ct}-{g_id}.gp'
	fsvg = f'svg/{ct}-{g_id}.svg'
	fsvg1 = f'svg/{ct}-{g_id+10}.svg'
	fsvg2 = f'svg/{ct}-{g_id+11}.svg'
	freport = f'report/{ct}-{g_id}.html'

	x, y, model, forecast = fit_edo_shape(ct, cur, tag, paramp=paramp, forecast_days=forecast_days)

	if model.success == False:
		data_consolidated.append('n.a.')
		model_consolidated.append(None)

		dump_xy_dat(fdata,x,y)
		dump_svg(fgplot, fsvg,
					f'{text} for {rname} on {curdate}',
					'Days from the first infected',
					f'{ylabel}', fdata, 2, f"{rname} data",
					opt='colorsequence podo',
					txt1='NO FIT AVAILABLE FOR THE CURRENT DATA', point=True)
	else:
		chisqr = model.chisqr
		param = model.params
		data_consolidated.append(chisqr)
		model_consolidated.append(model)
		if tag == 'accCombined':
			x = x[:len(x)//2]
			y = y[:len(x)//2]
			nx = x if forecast is None else np.arange(len(forecast)//2)
		else:	
			nx = x if forecast is None else np.arange(len(forecast))
		dump_xyz_dat(fdata, nx, y, forecast)
		dump_svg2D(fgplot, fsvg,
					f'{text} for {rname} on {curdate}',
					'Days from the first infected',
					f'{ylabel}',
					fdata, 2, 3,
					f"{rname} data",
					f'{text}',
					opt='yrange [0<*:]',
					txt1=f'SIMDRQME',
					txt2=f'𝛘² = {chisqr:9.2}')
		S, Q, E, A, I, D, R, M = edo.eval_edo(param, 250)
		pop = param['pop'].value
		Sr = [x/pop for x in S]
		Qr = [x/pop for x in Q]
		Er = [x/pop for x in E]
		Ar = [x/pop for x in A]
		Ir = [x/pop for x in I]
		Dr = [x/pop for x in D]
		Rr = [x/pop for x in R]
		Mr = [x/pop for x in M]
		svg.dump_8_dat(fdatc, Sr, Qr, Er, Ar, Ir, Dr, Rr, Mr)
		svg.dump_svg8D(fsvg1, fsvg2, fdatc, f'SIMDRQME Compartment Model for {rname} on {curdate}',
						'days', 'perc. of pop.', ['S','Q','E','A','I','D','R','M'])

	if model != None:		
		with open(freport, 'w') as f:
			table_info = f'<tr><td>Success status</td><td>{model.success}</td></tr>'
			table_info += f'<tr><td>Abort status</td><td>{model.aborted}</td></tr>'
			table_info += f'<tr><td>Fit message</td><td>{model.message}</td></tr>'
			table_stat = '<tr> <td>' + model._repr_html_() + '</td></tr>'
			table_obs = f'<tr><th>Days from the first infected</th><th>{ylabel}</th><th>Model {ylabel}</th></tr>'
			if forecast != None:
				for i, j, k in itertools.zip_longest(nx, y, forecast, fillvalue='nan'):
					table_obs += f'<tr><td>{i}</td><td>{j}</td><td>{k:.0f}</td></tr>'
			else:
				for i, j in itertools.zip_longest(x, y, fillvalue='nan'):
					table_obs += f'<tr><td>{i}</td><td>{j}</td><td>n.a.</td></tr>'
			f.write(param_page1(rname, table_info, table_stat, table_obs,fsvg,fsvg1,fsvg2))
	return

def run_rolling_average(x, y, ct, g_id, avgsize, curdate, ylabel):
	rname = ct.replace('_', ' ')
	fdata = f'gpdata/dat/{ct}-{g_id}.dat'
	fgplot = f'gpdata/{ct}-{g_id}.gp'
	fsvg = f'svg/{ct}-{g_id}.svg'
	freport = f'report/{ct}-{g_id}.html'

	dump_xy_dat(fdata,x,y)	

	dump_svg(fgplot, fsvg,
				f'7-Rolling average of cases for {rname} on {curdate}',
				f'Total {ylabel}',
				f'{avgsize}-rolling Average of {ylabel}',
				fdata, 2, f"{avgsize}-rolling average",
				opt='xrange [0<*:]\nset yrange [0<*:]',
				point=False, logx=True, logy=True)

	with open(freport, 'w') as f:
		table_info = f'<tr><td>Success on a {avgsize}-rolling average</td></tr>'
		table_stat = f'<tr><th>Day</th><th>{avgsize}-average of {ylabel}</th></tr>'
		for i, j in zip(x, y):
			table_stat += f'<tr><td>{i}</td><td>{j}</td></tr>'
		f.write(param_page(rname, table_info, table_stat, '<tr><td>None</td></tr>',fsvg))

	return 


def get_model_socnet(ct, g_id, curdate):
	rname = ct.replace('_', ' ')
	fdata = f'gpdata/dat/{ct}-{g_id}.dat'
	fgplot = f'gpdata/{ct}-{g_id}.gp'
	fsvg = f'svg/{ct}-{g_id}.svg'
	freport = f'report/{ct}-{g_id}.html'
	ylabel = 'Acc Infected'

	rname = ct.replace('_', ' ')
	if os.path.exists(fdata):
		dump_svg2D(fgplot, fsvg,
					f'SARS-COV-2-SOCNET Model for {rname} on {curdate}',
					'Days from the first infected',
					f'{ylabel}',
					fdata, 2, 3,
					f"{rname} data",
					f'SARS-COV-2-SOCNET Model',
					opt='yrange [0<*:]',
					txt1=f'SOCNET',
					txt2=f'𝛘² = n.a.')
	else:
		dump_svg_ph(fgplot, fsvg,
					f'SARS-COV-2-SOCNET Model for {rname} on {curdate}',
					'Days from the first infected', 'Acc Infected',
					txt1='NO MODE AVAILABLE FOR THE CURRENT DATA')
	return 

def run_socnet_model(x, y, ct, g_id, cur, tag, ylabel, data_consolidated, model_consolidated, curdate, text):
	import fitrs3
	from scipy.stats import chisquare
	rname = ct.replace('_', ' ')
	fdata = f'gpdata/dat/{ct}-{g_id}.dat'
	fgplot = f'gpdata/{ct}-{g_id}.gp'
	fsvg = f'svg/{ct}-{g_id}.svg'
	freport = f'report/{ct}-{g_id}.html'

	file1 = f'scnlog/{ct}-p1.dat'
	file2 = f'scnlog/{ct}-p2.dat'

	partition = len(y) // 4

	forecast = fitrs3.previsaoredeslp(y, 7, 200, 400, 100, file1, file2, partition, y[-1] + 50, y[-1] * 20, 4, 6, 0.2, 0.7, 0, 101)

	if forecast is None:
		data_consolidated.append('n.a.')
		data_consolidated.append('n.a.')

		dump_xy_dat(fdata,x,y)
		dump_svg(fgplot, fsvg,
					f'{text} for {rname} on {curdate}',
					'Days from the first infected',
					f'{ylabel}', fdata, 2, f"{rname} data",
					opt='colorsequence podo',
					txt1='NO FIT AVAILABLE FOR THE CURRENT DATA', point=True)
	else:
		chisqr = chisquare(y, f_exp=forecast[:len(y)])[0]
		data_consolidated.append(chisqr)
		model_consolidated.append('socnet-fitrs3')
		nx = x if forecast is None else np.arange(len(forecast))
		dump_xyz_dat(fdata, nx, y, forecast)
		dump_svg2D(fgplot, fsvg,
					f'{text} for {rname} on {curdate}',
					'Days from the first infected',
					f'{ylabel}',
					fdata, 2, 3,
					f"{rname} data",
					f'{text}',
					opt='yrange [0<*:]',
					txt1=f'SOCNET',
					txt2=f'𝛘² = {chisqr:9.2}')

	if forecast is not None:		
		with open(freport, 'w') as f:
			table_info = f'<tr><td>Success status</td><td>Forecast calculated with socnet-fitrs3</td></tr>'
			table_info += f'<tr><td>Abort status</td><td>n.a.</td></tr>'
			table_info += f'<tr><td>Fit message</td><td>n.a.</td></tr>'
			table_stat = '<tr> <td>n.a</td></tr>'
			table_obs = f'<tr><th>Days from the first infected</th><th>{ylabel}</th><th>Model {ylabel}</th></tr>'
			if forecast != None:
				for i, j, k in itertools.zip_longest(nx, y, forecast, fillvalue='nan'):
					table_obs += f'<tr><td>{i}</td><td>{j}</td><td>{k:.0f}</td></tr>'
			else:
				for i, j in itertools.zip_longest(x, y, fillvalue='nan'):
					table_obs += f'<tr><td>{i}</td><td>{j}</td><td>n.a.</td></tr>'
			f.write(param_page(rname, table_info, table_stat, table_obs,fsvg))
	return

def run_data(x, y, ct, g_id, ylabel, curdate, text, txt1=''):
	rname = ct.replace('_', ' ')
	fdata = f'gpdata/dat/{ct}-{g_id}.dat'
	fgplot = f'gpdata/{ct}-{g_id}.gp'
	fsvg = f'svg/{ct}-{g_id}.svg'
	dump_xy_dat(fdata,x,y)
	dump_svg(fgplot, fsvg,
				f'{text} for {rname} on {curdate}',
				'Days from the first infected',
				f'{ylabel}', fdata, 2, f"{rname} data",
				opt='colorsequence podo',
				txt1=txt1, point=True)

def notebook_run_edo(ct, database, tag, g_id, forecast_days):
	data = pd.DataFrame(database[ct]['DATA'])
	curdate = database[ct]['DATE']
	data_consolidated = list()
	model_consolidated = list()
	x = data['eDay'].values
	y = data['accCases'].values

	ylabel = 'Acc Infected'
	run_edo_model(ct, g_id, data, tag,
					ylabel, data_consolidated, model_consolidated,
					curdate, 'SIMDRQME Model on cases', forecast_days=forecast_days)
	
	tag2 = 'accCases' if tag == 'accDeaths' else 'accDeaths'
	x, y, params1, func1, ffunc1 = get_edo_config(ct, data, tag2, None)
	fy = ffunc1(model_consolidated[0].params, forecast_days)
	xd = data['eDay'].values
	yd = data['accDeaths'].values
	g_id += 1
	rname = ct.replace('_', ' ')
	fdata = f'gpdata/dat/{ct}-{g_id}.dat'
	fgplot = f'gpdata/{ct}-{g_id}.gp'
	fsvg = f'svg/{ct}-{g_id}.svg'

	dump_xyz_dat(fdata,xd,yd,fy)
	text = 'SIMDRQME Model'
	ylabel = 'Acc Deaths'
	dump_svg2D(fgplot, fsvg,
				f'{text} for {rname} on {curdate}',
				'Days from the first infected',
				f'{ylabel}',
				fdata, 2, 3,
				f"{rname} data",
				f'{text}',
				opt='yrange [0<*:]',
				txt1=f'SIMDRQME Model on deaths',
				txt2=f'𝛘² = n.a.')

	return model_consolidated[0].params