from .data import SimulationEvent
from .algo import calculate
import psutil
from multiprocessing import Pool

calc_func = None
calc_func_vaccineted = None
num_cpu = None


def calculate_infected(duration: int,
                       population_size: int,
                       gamma: float,
                       percentage_in_quarantine: float,
                       samples: int,
                       max_in_quarantine: int,
                       max_transmission_day: int,
                       i0active: int,
                       i0recovered: int) -> SimulationEvent:
    """Returns SimulationEvent
    args: duration, population_size, gamma, percentage_in_quarantine, samples, max_in_quarantine, max_transmission_day, i0active, i0recovered
    Evolves the social network dynamics for a population with gamma as parameter for a power law.
    """
    global calc_func
    simul = SimulationEvent(duration, population_size,
                            gamma, percentage_in_quarantine, max_in_quarantine, i0active, i0recovered)

    ret = calc_func(duration, population_size, i0active, i0recovered,
                    samples, max_transmission_day, max_in_quarantine,
                    gamma, percentage_in_quarantine)

    simul.mean = ret[0]
    simul.m2 = ret[1]
    simul.count = ret[2]
    simul.R_0 = ret[6]

    return simul

def calculate_infected_with_vaccine(duration: int,
                       population_size: int,
                       gamma: float,
                       percentage_in_quarantine: float,
                       samples: int,
                       max_in_quarantine: int,
                       max_transmission_day: int,
                       i0active: int,
                       i0recovered: int,
                       vaccinated_share: float,
                       vaccine_efficacy: float) -> SimulationEvent:
    """Returns SimulationEvent
    args: duration, population_size, gamma, percentage_in_quarantine, samples, max_in_quarantine, max_transmission_day, i0active, i0recovered
    Evolves the social network dynamics for a population with gamma as parameter for a power law.
    """
    global calc_func_vaccineted
    simul = SimulationEvent(duration, population_size,
                            gamma, percentage_in_quarantine, max_in_quarantine, i0active, i0recovered)

    ret = calc_func_vaccineted(duration, population_size, i0active, i0recovered,
                    samples, max_transmission_day, max_in_quarantine,
                    gamma, percentage_in_quarantine, vaccinated_share, vaccine_efficacy)

    simul.mean = ret[0]
    simul.m2 = ret[1]
    simul.count = ret[2]
    simul.R_0 = ret[6]

    return simul



def init_algo(s: str) -> None:
    global calc_func, calc_func_vaccineted
    if s == 'FAST':
        calc_func = calculate.calculate_infection
        calc_func_vaccineted = calculate.calculate_infection_with_vaccine
    else:
        calc_func = calculate.calculate_infection
        calc_func_vaccineted = calculate.calculate_infection_with_vaccine
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
