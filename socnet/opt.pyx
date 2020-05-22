import numpy as np
import random
import math
from .simul import calculate_infected

def best_fit(data_set, int start_day, int end_day, int i0_size, int i0_recovered, int samples, 
                int nrevision, int num_ressample, file_name, int seed, int pop_min, int pop_max, double min_error):
    cdef int duration, max_quarentine_low, max_quarentine_high, pop_size_low, pop_size_high
    cdef int max_in_quarentine, population_size, parte
    cdef double perc_quarentine_low, perc_quarentine_high, gamma_low, gamma_high, perc_quarentine
    cdef double gamma, mse, corr

    random.seed(seed)

    current_data = np.array(data_set[start_day:end_day])

    duration = end_day - start_day

    RF = open("r0" + file_name.replace("result",""), 'w')
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

    max_quarentine_low = 2
    max_quarentine_high = 12
    max_quarentine_search_list = []

    perc_quarentine_low = 0.01
    perc_quarentine_high = 0.99
    perc_quarentine_search_list = []

    gamma_low = 3.5
    gamma_high = 5.5
    gamma_search_list = []

    pop_size_low = pop_min
    pop_size_high = pop_max
    pop_size_search_list = []

    error = min_error

    resample_tmp = 0
    sample_number = 1

    for n in range(nrevision):
        if (n % 2 == 0):
            print( n )
        resample_tmp += 1

        max_in_quarentine = random.randint( max_quarentine_low, max_quarentine_high)       # sorteio - limites (3,10)
        perc_quarentine = perc_quarentine_low + random.random() * (perc_quarentine_high-perc_quarentine_low) # sorteio - limites (0,1)
        gamma = gamma_low + random.random() * (gamma_high - gamma_low)           # sorteio - limites (3.5-5.5)
        population_size = random.randint(pop_size_low, pop_size_high)

        simul = calculate_infected(duration, population_size, gamma,perc_quarentine, samples, max_in_quarentine, 14, i0_size, i0_recovered)
        
        mse = math.sqrt((np.square(current_data - simul.mean)).mean())
        corr = np.corrcoef(current_data,simul.mean)[0][1]

        if(mse < error):
            print(f'\nErro - {mse:5.2}\n')
            print(f'Coeficiente - {gamma:5.5}\n')
            print(f'Parcela em quarentena - {perc_quarentine:5.5}\n')
            print(f'Tamanho da Populacao - {population_size:5}\n')
            print(f'Max. infectados em quarentena - {max_in_quarentine:5}\n')
            print(f'Correlação de Pearson = {corr:5.5}')

            resample_tmp = 0
            error = mse

            F.write('{0:5.5f};'.format(gamma))
            F.write('{0:5.5f};'.format(perc_quarentine))
            F.write('{0:5d};'.format(population_size))
            F.write('{0:5d};'.format(max_in_quarentine))
            F.write('{0:5.5f};'.format(error))

            RF.write('{0:5.5f};'.format(gamma))
            RF.write('{0:5.5f};'.format(perc_quarentine))
            RF.write('{0:5d};'.format(population_size))
            RF.write('{0:5d};'.format(max_in_quarentine))
            RF.write('{0:5.5f};'.format(error))

            max_quarentine_search_list.append(max_in_quarentine)
            perc_quarentine_search_list.append(perc_quarentine)
            gamma_search_list.append(gamma)
            pop_size_search_list.append(population_size)

            for m in range(duration):
                F.write('{0:5.5f};'.format(simul.mean[m]))
            F.write('\n')

            
            RF.write('{0:5.5f};'.format(simul.R_0[m]))
            RF.write('{0:5.5f};'.format(corr))
            RF.write('\n')

            if (max_in_quarentine >= round((max_quarentine_low + max_quarentine_high)/2, 0)):
                max_quarentine_high = max_in_quarentine
            else:
                max_quarentine_low = max_in_quarentine

            if (perc_quarentine > (perc_quarentine_low + perc_quarentine_high)/2):
                perc_quarentine_high = perc_quarentine
            else:
                perc_quarentine_low = perc_quarentine

            if (gamma > (gamma_low + gamma_high)/2):
                gamma_high = gamma
            else:
                gamma_low = gamma

            if (population_size >= round((pop_size_low + pop_size_high)/2, 0)):
                pop_size_high = population_size
            else:
                pop_size_low = population_size

        if ((resample_tmp % num_ressample == 0) and len(max_quarentine_search_list) > 2):
            print('Ressorteio!')
            parte = (sample_number % 4) / 4
            max_quarentine_low = round(2 + parte * (min(max_quarentine_search_list) - 3))
            max_quarentine_high = round(max(max_quarentine_search_list) + parte * (12 - max(max_quarentine_search_list)))
            perc_quarentine_low = 0.01 + parte * (min(perc_quarentine_search_list) - 0.01)
            perc_quarentine_high = max(perc_quarentine_search_list) + parte * (0.99 - max(perc_quarentine_search_list))
            gamma_low = 3.5 + parte * (min(gamma_search_list) - 3.5)
            gamma_high = max(gamma_search_list) + parte * (5.5 - max(gamma_search_list))
            pop_size_low = round(pop_min + parte * (min(pop_size_search_list) - pop_min))
            pop_size_high = round(max(pop_size_search_list) + parte * (pop_max - max(pop_size_search_list)))
            resample_tmp = 1
            sample_number += 1

        if (sample_number % 4 == 0):
            print('Revisão!')
            max_quarentine_low = 2
            max_quarentine_high = 12
            perc_quarentine_low = 0.01
            perc_quarentine_high = 0.99
            gamma_low = 3.5
            gamma_high = 5.5
            pop_size_low = 5000
            pop_size_high = 50000000
            resample_tmp = 0
            sample_number += 1

    print('\nPronto!')
    F.close()
    RF.close()

