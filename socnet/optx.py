from .simul import calculate_infected, init_algo
from .data import SimulationParams2
import numpy as np
import pandas as pd
import math
import random
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error


def f_gamma(x, *argv):
    gamma = x[0]
    #population_size = int(round(x[0]))
    #percentage_in_quarentine = x[1]
    #max_in_quarentine = int(x[2])

    duration = argv[0]
    population_size = argv[1]
    samples = argv[2]
    max_transmission_day = argv[3]
    real_val = argv[4]
    #gamma = argv[5]
    percentage_in_quarentine = argv[6]
    max_in_quarentine = argv[7]
    i0a = argv[8]
    i0r = argv[9]

    s = calculate_infected(duration, population_size, gamma,
                           percentage_in_quarentine,
                           samples, max_in_quarentine,
                           max_transmission_day, i0a, i0r)

    model_val = np.array(s.mean)
    mse = math.sqrt(mean_squared_error(real_val, s.mean))
    print(f'f_gamma: {x} -> {mse}')
    return mse


def f_pop(x, *argv):
    #gamma = x[0]
    population_size = int(round(x[0]))
    #percentage_in_quarentine = x[1]
    #max_in_quarentine = int(x[2])

    duration = argv[0]
    #population_size = argv[1]
    samples = argv[2]
    max_transmission_day = argv[3]
    real_val = argv[4]
    gamma = argv[5]
    percentage_in_quarentine = argv[6]
    max_in_quarentine = argv[7]
    i0a = argv[8]
    i0r = argv[9]

    s = calculate_infected(duration, population_size, gamma,
                           percentage_in_quarentine,
                           samples, max_in_quarentine,
                           max_transmission_day, i0a, i0r)

    model_val = np.array(s.mean)
    mse = math.sqrt(mean_squared_error(real_val, s.mean))
    print(f'f_pop: {x} -> {mse}')
    return mse


def find_x0(param, samples):
    gamma = 3.0
    s = calculate_infected(param.duration, param.population_size, gamma,
                           0.0,
                           samples, 0,
                           param.max_transmission_day, param.i0a, param.i0r)
    mse = math.sqrt(mean_squared_error(param.real_data, s.mean))
    print(f'find_x0: {gamma} -> {mse}.')

    for g in [3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]:
        s = calculate_infected(param.duration, param.population_size, gamma,
                           0.0,
                           samples, 0,
                           param.max_transmission_day, param.i0a, param.i0r)
        new_mse = math.sqrt(mean_squared_error(param.real_data, s.mean))
        print(f'find_x0: {g} -> {new_mse}.')
        if new_mse < mse:
            mse = new_mse
            gamma = g
    print(f'find_x0: FINAL {gamma} -> {mse}.')
    return gamma

def best_fit(data_set, start_day, end_day, i0_size, i0_recovered, samples,
             nrevision, num_ressample, file_name, seed, pop_min, pop_max, min_error):

    RF = open('r0' + file_name.replace("result", ""), 'w')
    F = open(file_name, 'w')

    F.write('Modelo de Redes Sociais - Adaptativo\n')
    F.write('Parametros;;;;;Dados (primeira linha - dados reais)\n')
    F.write('Coeficiente;Parcela_em_quarentena;Tam_Pop;Max_contagio;Erro;')

    RF.write('Modelo de Redes Sociais - Adaptativo - Calculo do R_0\n')
    RF.write('Parametros;;;;;Dados (primeira linha - dados reais)\n')
    RF.write('Coeficiente;Parcela_em_quarentena;Tam_Pop;Max_contagio;Erro;')

    for n in range(start_day, end_day):
        F.write('{0:5d};'.format(data_set[n]))
        RF.write('{0:5d};'.format(n))
    F.write('\n')
    RF.write('\n')

    current_data = np.array(data_set[start_day:end_day])
    duration = end_day - start_day
    population_size = pop_max
    max_transmission_day = 14
    real_data = current_data
    #gamma
    #percent_quarentine 
    #max_quarentine
    i0a = i0_size
    i0r = i0_recovered

    #first, find the best gamma in the valey
    init_algo('FAST')
    param_gamma = SimulationParams2(duration=duration, population_size=population_size, gamma=0,
                                    percent_quarentine=0.0, samples=samples, max_quarentine=0,
                                    max_transmission_day=max_transmission_day,
                                    real_data=real_data, i0a=i0a, i0r=i0r)
    options_gamma = {'fatol': 5.0, 'xatol': 1, 'maxiter': 100, 'disp': True}
    x0 = [find_x0(param_gamma,samples)]
    res_gamma = minimize(f_gamma, x0, args=param_gamma,method='Nelder-Mead', options=options_gamma)
    gamma = res_gamma.x[0]

    mse = res_gamma.fun  # Since Mont Carlo, perhaps...
    mse_p = 2 * mse

    pop_x0 = current_data[-1] + (i0a+i0r)
    while mse_p > mse:
        #second, find the best population from min to max
        param_pop = SimulationParams2(duration=duration, population_size=0, gamma=gamma, percent_quarentine=0.0,
                                        samples=samples, max_quarentine=0, max_transmission_day=14,
                                        real_data=real_data, i0a=i0a, i0r=i0r)
        options_pop = {'fatol': 5.0, 'xatol': 10000, 'maxiter': 20, 'disp': True}
        x0 = [pop_x0]
        res_pop = minimize(f_pop, x0, args=param_pop, method='Nelder-Mead', options=options_pop)
        population_size = int(round(res_pop.x[0]))
        pop_x0 += pop_max//100
        mse_p = res_pop.fun
        if pop_x0 > pop_max:
            break


    init_algo('STANDARD')
    s = calculate_infected(duration, pop_max, gamma, 0.0, samples, 0, max_transmission_day, i0a, i0r)
    mse = res_gamma.fun  # Since Mont Carlo, perhaps...
    corr = np.corrcoef(current_data, s.mean)[0][1]

    F.write(f'{gamma:5.5f}; 0.0;{pop_max:5d}; 0; {mse:5.5f};')
    RF.write(f'{gamma:5.5f}; 0.0;{pop_max:5d}; 0; {mse:5.5f};')
    for m in range(duration):
        F.write(f'{s.mean[m]:5.5f};')
    F.write('\n')
    RF.write(f'{s.R_0[m]:5.5f}; {corr:5.5f};\n')

    s = calculate_infected(duration, population_size, gamma, 0.0, samples, 0, max_transmission_day, i0a, i0r)
    mse = res_pop.fun  # Since Mont Carlo, perhaps...
    corr = np.corrcoef(current_data, s.mean)[0][1]

    F.write(f'{gamma:5.5f}; 0.0;{population_size:5d}; 0; {mse:5.5f};')
    RF.write(f'{gamma:5.5f}; 0.0;{population_size:5d}; 0; {mse:5.5f};')
    for m in range(duration):
        F.write(f'{s.mean[m]:5.5f};')
    F.write('\n')
    RF.write(f'{s.R_0[m]:5.5f}; {corr:5.5f};\n')

    for percent in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        for max_q in [1, 2, 3, 4, 7, 9, 13]:
            s = calculate_infected(duration,
                              population_size, gamma,
                              percent,
                              samples, max_q,
                              max_transmission_day, i0a, i0r)
            mse = math.sqrt(mean_squared_error(current_data, s.mean))
            corr = np.corrcoef(current_data, s.mean)[0][1]
            print(f'best_fit: {gamma} {population_size} {percent} {max_q} -> {mse}')
            F.write('{0:5.5f};'.format(gamma))
            F.write('{0:5.5f};'.format(percent))
            F.write('{0:5d};'.format(population_size))
            F.write('{0:5d};'.format(max_q))
            F.write('{0:5.5f};'.format(mse))

            RF.write('{0:5.5f};'.format(gamma))
            RF.write('{0:5.5f};'.format(percent))
            RF.write('{0:5d};'.format(population_size))
            RF.write('{0:5d};'.format(max_q))
            RF.write('{0:5.5f};'.format(mse))
 
            for m in range(duration):
                F.write('{0:5.5f};'.format(s.mean[m]))
            F.write('\n')

            RF.write('{0:5.5f};'.format(s.R_0[m]))
            RF.write('{0:5.5f};'.format(corr))
            RF.write('\n')
