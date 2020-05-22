from .simul import init, calculate_infected
from .data import SimulationEvent

def test_fast():
	#init('FAST')
	s = calculate_infected(100, 1000, 3.5, 0, 100000, 0, 14, 1, 0)

	for i in s.mean:
		print(i)

	return