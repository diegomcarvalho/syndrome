#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

namespace py = pybind11;

void
init_module();
std::vector<std::vector<double>>
calculate_infection(const int duration,
                    const int susceptible_max_size,
                    const int i0active,
                    const int i0recovered,
                    const int samples,
                    const int max_transmission_day,
                    const int max_in_quarantine,
                    const double gamma,
                    const double percentage_in_quarantine);
std::vector<std::vector<double>>
calculate_infection_varying_perc(
  const int duration,
  const int susceptible_max_size,
  const int i0active,
  const int i0recovered,
  const int samples,
  const int max_transmission_day,
  const int max_in_quarantine,
  const double gamma,
  const std::vector<double> percentage_in_quarantine,
  const bool recont);

PYBIND11_MODULE(calculate, m)
{
    m.doc() =
      "calculate_infection implemented in C++"; // optional module docstring

    /*     m.def("pl", &pl, "powerlaw tester.");
        m.def("ds", &ds, "powerlaw tester.");
     */
    m.def("init_module", &init_module, "Initialize the Random Number Generator.");
    m.def("calculate_infection", &calculate_infection, "Simulate the Social Network Model for SIRE dynamics.");
    m.def("calculate_infection_varying_perc", &calculate_infection_varying_perc, "Simulate the Social Network Model for SIRE dynamics.");
}
