from .data import SimulationEvent
from .algo import calculate
import psutil
from multiprocessing import Pool

calc_func = None
calc_func_varing = None
num_cpu = None


def calculate_infected(duration: int,
                       population_size: int,
                       gamma: float,
                       percentage_in_quarentine: float,
                       samples: int,
                       max_in_quarentine: int,
                       max_transmission_day: int,
                       i0active: int,
                       i0recovered: int) -> SimulationEvent:
    """Returns SimulationEvent
    args: duration, population_size, gamma, percentage_in_quarentine, samples, max_in_quarentine, max_transmission_day, i0active, i0recovered
    Evolves the social network dynamics for a population with gamma as parameter for a power law.
    """
    global calc_func
    simul = SimulationEvent(duration, population_size,
                            gamma, percentage_in_quarentine, max_in_quarentine, i0active, i0recovered)

    ret = calc_func(duration, population_size, i0active, i0recovered,
                    samples, max_transmission_day, max_in_quarentine,
                    gamma, percentage_in_quarentine)

    simul.mean = ret[0]
    simul.m2 = ret[1]
    simul.count = ret[2]
    simul.R_0 = ret[6]

    return simul


def p_calculate_infected(duration, population_size,  gamma,  percentage_in_quarentine,  samples,  max_in_quarentine,  max_transmission_day,  i0active,  i0recovered) -> SimulationEvent:
    """Returns SimulationEvent
    args: duration, population_size, gamma, percentage_in_quarentine, samples, max_in_quarentine, max_transmission_day, i0active, i0recovered
    Evolves the social network dynamics for a population with gamma as parameter for a power law.
    """
    global calc_func, num_cpu

    print(num_cpu)
    res = None
    psample = samples // num_cpu
    simul = SimulationEvent(duration, population_size, gamma,
                            percentage_in_quarentine, max_in_quarentine, i0active, i0recovered)
    param = [(duration, population_size, gamma, percentage_in_quarentine,
              psample, max_in_quarentine, max_transmission_day, i0active, i0recovered) for _ in range(num_cpu)]

    with Pool(processes=num_cpu) as p:
        results = p.starmap(calculate_infected, param)

    for ret in results:
        simul.mean += ret.mean / num_cpu
        simul.m2 += ret.m2 / num_cpu
        simul.count += ret.count
        simul.R_0 += ret.R_0 / num_cpu

    return simul


def calculate_infected_varying(duration: int,
                                population_size: int,
                                gamma: float,
                                percentage_in_quarentine: list,
                                samples: int,
                                max_in_quarentine: int,
                                max_transmission_day: int,
                                i0active: list,
                                i0recovered: list,
                                recalculate: bool) -> SimulationEvent:
    """Returns SimulationEvent
    args: duration, population_size, gamma, percentage_in_quarentine, samples, max_in_quarentine, max_transmission_day, i0active, i0recovered
    Evolves the social network dynamics for a population with gamma as parameter for a power law.
    """
    global calc_func_varing
    simul = SimulationEvent(duration, population_size,
                            gamma, percentage_in_quarentine, max_in_quarentine, i0active, i0recovered)

    ret = calc_func_varing(duration, population_size, i0active, i0recovered, samples, max_transmission_day, max_in_quarentine,
                           gamma, percentage_in_quarentine, recalculate)

    simul.mean = ret[0]
    simul.m2 = ret[1]
    simul.count = ret[2]
    simul.R_0 = ret[6]

    return simul


def p_calculate_infection_varying_perc(duration: int,
                                       population_size: int,
                                       gamma: float,
                                       percentage_in_quarentine: float,
                                       samples: int,
                                       max_in_quarentine: int,
                                       max_transmission_day: int,
                                       i0active: int,
                                       i0recovered: int) -> SimulationEvent:
    """Returns SimulationEvent
    args: duration, population_size, gamma, percentage_in_quarentine, samples, max_in_quarentine, max_transmission_day, i0active, i0recovered
    Evolves the social network dynamics for a population with gamma as parameter for a power law.
    """
    global calc_func, num_cpu

    print(num_cpu)
    res = None
    psample = samples // num_cpu
    simul = SimulationEvent(duration, population_size, gamma,
                            percentage_in_quarentine, max_in_quarentine, i0active, i0recovered)
    param = [(duration, population_size, gamma, percentage_in_quarentine,
              psample, max_in_quarentine, max_transmission_day, i0active, i0recovered) for _ in range(num_cpu)]

    with Pool(processes=num_cpu) as p:
        results = p.starmap(calculate_infected_varying, param)

    for ret in results:
        simul.mean += ret.mean / num_cpu
        simul.m2 += ret.m2 / num_cpu
        simul.count += ret.count
        simul.R_0 += ret.R_0 / num_cpu

    return simul


def init_algo(s: str) -> None:
    global calc_func, calc_func_varing
    if s == 'FAST':
        calc_func = calculate.calculate_infection
        calc_func_varing = calculate.calculate_infected_varying
    else:
        calc_func = calculate.calculate_infection
        calc_func_varing = calculate.calculate_infected_varying
    return


def __init__():
    global calc_func, num_cpu
    # print("=====================================")
    #print("===     Initing SocNetOpt C++     ===")
    # print("=====================================")
    # print("")
    #print("-> Initing the random generator...")
    calculate.init_module()
    init_algo('STANDARD')
    num_cpu = psutil.cpu_count(logical=True)


__init__()
