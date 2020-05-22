from collections import namedtuple
import numpy as np

SimulationParams = namedtuple(
    'SimulationParams',
    ['duration',
     'population_size',
     'samples',
     'max_transmission_day',
     'real_data',
     'gamma',
     'percent_quarentine',
     'max_quarentine'])

SimulationParams2 = namedtuple(
    'SimulationParams',
    ['duration',
     'population_size',
     'samples',
     'max_transmission_day',
     'real_data',
     'gamma',
     'percent_quarentine',
     'max_quarentine', 'i0a', 'i0r'])

class SimulationEvent(object):
    def __init__(self, duration, pop_size, gamma,  percent_quarentine,  max_quarentine,  i0active,  i0recovered):
        self._duration = duration
        self._pop_size = pop_size
        self._gamma = gamma
        self._percent_quarentine = percent_quarentine
        self._max_quarentine = max_quarentine
        self._i0active = i0active
        self._i0recovered = i0recovered
        self._mean = np.zeros(duration)
        self._count = np.zeros(duration)
        self._m2 = np.zeros(duration)
        self._R_0 = np.zeros(duration)
        self._rcount = np.zeros(duration)
        self._iEactive = 0
        self._iErecovered = 0
        return

    def __str__(self):
     return (f"SimulationEvent(\n"
             f"\t duration       ={self._duration},\n"
             f"\t population     ={self._pop_size},\n"
             f"\t gamma          ={self._gamma},\n"
             f"\t perc_quarntine ={self._percent_quarentine},\n"
             f"\t max_quarentine ={self._max_quarentine},\n"
             f"\t i0 active      ={self._i0active},\n"
             f"\t i0 recoververd ={self._i0recovered})\n\n"
             f"mean={self._mean}\n"
             f"  m2={self._m2}\n"
             f"count={self._count}\n")

    @property
    def duration(self):
        return self._duration

    @property
    def pop_size(self):
        return self._pop_size

    @property
    def gamma(self):
        return self._gamma

    @property
    def percent_quarentine(self):
        return self._percent_quarentine

    @property
    def max_quarentine(self):
        return self._max_quarentine

    @property
    def R_0(self):
        return self._R_0

    @R_0.setter
    def R_0(self, value):
        self._R_0 = np.array(value)

    def add_value(self, id, value):
        delta = value - self._mean[id]
        self._count[id] += 1
        self._mean[id] += delta / self._count[id]
        delta2 = value - self._mean[id]
        self._m2[id] += delta * delta2

    def add_R_0(self, id, value):
        delta = value - self._R_0[id]
        self._rcount[id] += 1
        self._R_0[id] += delta / self._rcount[id]

    @property
    def mean(self):
        return self._mean

    @mean.setter
    def mean(self, val):
        self._mean = np.array(val)

    @property
    def m2(self):
        return self._m2

    @m2.setter
    def m2(self, val):
        self._m2 = np.array(val)

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, val):
        self._count = np.array(val)

    @property
    def variance(self):
        return self._m2 / (self._count)

    @property
    def sdev(self):
        return np.sqrt(self._m2 / (self._count))

    @property
    def sderror(self):
        return (np.sqrt(self._m2 / (self._count))) / np.sqrt(self._count)
