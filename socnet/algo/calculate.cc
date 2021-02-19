#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include <algorithm>
#include <cmath>
#include <iostream>
#include <memory>
#include <random>

#include "population.hpp"
#include "statistics.hpp"

std::mt19937_64 my_gen; // Standard mersenne_twister_engine seeded with rd()

inline int
powerlaw(double gamma, double ran)
{
    return int((pow(ran, (-1.0 / gamma))) - 0.5);
}

inline int
find_first(Population& population)
{
    int size = population.size();
    int first = size - 1;

    for (int k = 0; k < size; k++) {
        if (population[k].is_active()) {
            first = k;
            break;
        }
    }
    return first;
}

void
init_module()
{
    // std::cout << "calculate.cc - random setup done." << std::endl;
    my_gen.seed(100);
    return;
}

int
vaccinate(const int individuals,
          const double vaccinated_percentage,
          const double vaccine_efficacy)
{
    int immune_individuals = 0;
    double real_efficacy = vaccinated_percentage * vaccine_efficacy;

    std::uniform_real_distribution<> dis(0.0, 1.0);

    for (auto i = 0; i < individuals; i++) {
        immune_individuals += (dis(my_gen) < real_efficacy);
    }
    return immune_individuals;
}

std::vector<std::vector<double>>
calculate_infection(const int duration,
                    const int susceptible_max_size,
                    const int i0active,
                    const int i0recovered,
                    const int samples,
                    const int max_transmission_day,
                    const int max_in_quarantine,
                    const double gamma,
                    const double percentage_in_quarantine)
{
    std::uniform_real_distribution<> dis(0.0, 1.0);
    std::uniform_int_distribution<> i_dis(
      0, susceptible_max_size + i0active + i0recovered);

    int S, I;

    Population population(susceptible_max_size + i0active + i0recovered);

    Statistics<double> infected_stat(duration, 0.0);
    Statistics<double> susceptible_stat(duration, 0.0);
    Statistics<double> r_0_stat(duration, 0.0);

    for (int k = 0; k < samples; k++) {
        population.seed_infected(i0active,
                                 i0recovered,
                                 percentage_in_quarantine,
                                 max_transmission_day);
        S = susceptible_max_size - i0active - i0recovered;

        for (int day = 0; day < duration; day++) {
            I = population.size();

            infected_stat.add_value(day, double(I));
            susceptible_stat.add_value(day, double(S));

            for (int ind = population.first_subject(); ind < I; ind++) {
                auto& person = population[ind];

                if (person.is_active()) {
                    if (person.days_of_infection < max_transmission_day) {
                        person.days_of_infection++;
                        int available_new_infected =
                          powerlaw(gamma, dis(my_gen));

                        if (!available_new_infected)
                            continue;

                        if (person.is_quarantined())
                            available_new_infected =
                              std::min(max_in_quarantine - person.decendants,
                                       available_new_infected);

                        int new_infected = 0;
                        for (int ni = 0; ni < available_new_infected; ni++) {
                            // Check if the individual belongs to S, and
                            if ((i_dis(my_gen) < S) && (S > 0)) {
                                new_infected++;
                                S--;
                                population.new_subject(
                                  0,
                                  ind,
                                  day,
                                  true,
                                  (dis(my_gen) < percentage_in_quarantine));
                            }
                        }
                        person.decendants += new_infected;
                    } else {
                        person.clear_active();
                        if (population.first_subject() == (ind - 1))
                            population.move_first(ind);
                    }
                }
            }
            int kp = 0, dp = 0;
            for (unsigned int ui = 0; ui < population.size(); ui++) {
                // for (auto person : population)
                auto& person = population[ui];
                if ((person.parent == -1) ||
                    (person.days_of_infection < max_transmission_day))
                    continue;
                kp++;
                dp += person.decendants;
            }
            if (kp)
                r_0_stat.add_value(day, double(dp) / double(kp));
        }
        population.reset_population();
    }

    std::vector<std::vector<double>> res;

    res.push_back(infected_stat.get_mean());  // 0
    res.push_back(infected_stat.get_m2());    // 1
    res.push_back(infected_stat.get_count()); // 2

    res.push_back(susceptible_stat.get_mean());  // 3
    res.push_back(susceptible_stat.get_m2());    // 4
    res.push_back(susceptible_stat.get_count()); // 5

    res.push_back(r_0_stat.get_mean());  // 6
    res.push_back(r_0_stat.get_m2());    // 7
    res.push_back(r_0_stat.get_count()); // 8

    return res;
}

std::vector<std::vector<double>>
calculate_infection_with_vaccine(const int duration,
                                 const int susceptible_max_size,
                                 const int i0active,
                                 const int i0recovered,
                                 const int samples,
                                 const int max_transmission_day,
                                 const int max_in_quarantine,
                                 const double gamma,
                                 const double percentage_in_quarantine,
                                 const double vaccinated_share,
                                 const double vaccine_efficacy)
{
    std::uniform_real_distribution<> dis(0.0, 1.0);
    std::uniform_int_distribution<> i_dis(
      0, susceptible_max_size + i0active + i0recovered);

    int S, I;

    Population population(susceptible_max_size + i0active + i0recovered);

    Statistics<double> infected_stat(duration, 0.0);
    Statistics<double> susceptible_stat(duration, 0.0);
    Statistics<double> r_0_stat(duration, 0.0);

    for (int k = 0; k < samples; k++) {
        population.seed_infected(i0active,
                                 i0recovered,
                                 percentage_in_quarantine,
                                 max_transmission_day);
        S = susceptible_max_size - i0active - i0recovered;

        for (int day = 0; day < duration; day++) {
            I = population.size();

            infected_stat.add_value(day, double(I));
            susceptible_stat.add_value(day, double(S));

            for (int ind = population.first_subject(); ind < I; ind++) {
                auto& person = population[ind];

                if (person.is_active()) {
                    if (person.days_of_infection < max_transmission_day) {
                        person.days_of_infection++;
                        int available_new_infected =
                          powerlaw(gamma, dis(my_gen));
                        available_new_infected -=
                          vaccinate(available_new_infected,
                                    vaccinated_share,
                                    vaccine_efficacy);
                        if (!available_new_infected)
                            continue;

                        if (person.is_quarantined())
                            available_new_infected =
                              std::min(max_in_quarantine - person.decendants,
                                       available_new_infected);

                        int new_infected = 0;
                        for (int ni = 0; ni < available_new_infected; ni++) {
                            // Check if the individual belongs to S, and
                            if ((i_dis(my_gen) < S) && (S > 0)) {
                                new_infected++;
                                S--;
                                population.new_subject(
                                  0,
                                  ind,
                                  day,
                                  true,
                                  (dis(my_gen) < percentage_in_quarantine));
                            }
                        }
                        person.decendants += new_infected;
                    } else {
                        person.clear_active();
                        if (population.first_subject() == (ind - 1))
                            population.move_first(ind);
                    }
                }
            }
            int kp = 0, dp = 0;
            for (unsigned int ui = 0; ui < population.size(); ui++) {
                // for (auto person : population)
                auto& person = population[ui];
                if ((person.parent == -1) ||
                    (person.days_of_infection < max_transmission_day))
                    continue;
                kp++;
                dp += person.decendants;
            }
            if (kp)
                r_0_stat.add_value(day, double(dp) / double(kp));
        }
        population.reset_population();
    }

    std::vector<std::vector<double>> res;

    res.push_back(infected_stat.get_mean());  // 0
    res.push_back(infected_stat.get_m2());    // 1
    res.push_back(infected_stat.get_count()); // 2

    res.push_back(susceptible_stat.get_mean());  // 3
    res.push_back(susceptible_stat.get_m2());    // 4
    res.push_back(susceptible_stat.get_count()); // 5

    res.push_back(r_0_stat.get_mean());  // 6
    res.push_back(r_0_stat.get_m2());    // 7
    res.push_back(r_0_stat.get_count()); // 8

    return res;
}
