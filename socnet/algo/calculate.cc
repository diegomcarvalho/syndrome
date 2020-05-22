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

// Random must be integrated into the init_random().
// std::random_device rd;	//Will be used to obtain a seed for the random
// number engine

std::mt19937_64 gen; // Standard mersenne_twister_engine seeded with rd()

inline int
powerlaw(int xmin, double coef, double ran)
{
    return int(std::round((xmin * pow(ran, (-1.0 / coef))) - 1));
}

inline int
find_first(Population& population)
{
    int size = population.size();
    int first = size - 1;

    for (int k = 0; k < size; k++) {
        if (population[k]->active == true) {
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
    gen.seed(100);
    return;
}

void
recontaminate(Population& population, double percentage)
{
    std::uniform_real_distribution<> dis(0.0, 1.0);

    for (unsigned int k = 0; k < population.size(); k++) {
        if (population[k]->active) {
            if (dis(gen) < percentage)
                population[k]->quarantine_status = true;
            else
                population[k]->quarantine_status = false;
        }
    }
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
    std::uniform_int_distribution<> idis(0, susceptible_max_size + i0active + i0recovered);

    int S, I;

    Population population(susceptible_max_size + i0active + i0recovered);

    Statistics<double> infected_stat(duration, 0.0);
    Statistics<double> susceptible_stat(duration, 0.0);
    Statistics<double> r_0_stat(duration, 0.0);

    for (int k = 0; k < samples; k++) {
        population.seed_infected(i0active, i0recovered, percentage_in_quarantine);
        S = susceptible_max_size - i0active - i0recovered;

        for (int day = 0; day < duration; day++) {
            I = population.size();

            infected_stat.add_value(day, double(I));
            susceptible_stat.add_value(day, double(S));

            for (int ind = population.first_individual(); ind < I; ind++) {
                auto person = population[ind];

                if (person->active) {
                    if (person->days_of_infection < max_transmission_day) {
                        person->days_of_infection++;
                        int available_new_infected = powerlaw(1, gamma, dis(gen));

                        if (!available_new_infected) continue;

                        if (person->quarantine_status)
                            available_new_infected = std::min(max_in_quarantine - person->decendants, available_new_infected);

                        int new_infected = 0;
                        for (int ni = 0; ni < available_new_infected; ni++) {
                            // Check if the individual belongs to S, and
                            if ((idis(gen) < S) && (S > 0)) {
                                bool quarantine = (dis(gen) < percentage_in_quarantine) ? true : false;
                                new_infected++;
                                S--;
                                population.new_individual(day, ind, true, Status::sick, quarantine);
                            }
                        }
                        person->decendants += new_infected;
                    } else {
                        person->active = false;
                        person->status = Status::recovered;
                        if (ind == population.first_individual()) population.move_first(ind);
                    }
                }
            }
            int kp = 0, dp = 0;
            for (unsigned int ui = 0; ui < population.size(); ui++) {
                // for (auto person : population)
                auto person = population[ui];
                if ((person->parent == -1) ||
                    (person->days_of_infection < max_transmission_day))
                    continue;
                kp++;
                dp += person->decendants;
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
calculate_infection_varying_perc(const int duration,
                                 const int susceptible_max_size,
                                 const int i0active,
                                 const int i0recovered,
                                 const int samples,
                                 const int max_transmission_day,
                                 const int max_in_quarantine,
                                 const double gamma,
                                 const std::vector<double> percentage_in_quarantine,
                                 const bool recont)
{
    std::uniform_real_distribution<> dis(0.0, 1.0);
    std::uniform_int_distribution<> idis(0, susceptible_max_size);

    int S, I;

    Population population(susceptible_max_size + i0active + i0recovered);

    Statistics<double> infected_stat(duration, 0.0);
    Statistics<double> susceptible_stat(duration, 0.0);
    Statistics<double> r_0_stat(duration, 0.0);

    for (int k = 0; k < samples; k++) {
        population.seed_infected(i0active, i0recovered, percentage_in_quarantine[0]);
        S = susceptible_max_size - i0active - i0recovered;

        for (int day = 0; day < duration; day++) {
            I = population.size();

            infected_stat.add_value(day, I);
            susceptible_stat.add_value(day, S);

            for (int ind = population.first_individual(); ind < I; ind++) {
                auto person = population[ind];

                if (person->active) {
                    if (person->days_of_infection < max_transmission_day) {
                        person->days_of_infection++;
                        int available_new_infected = powerlaw(1, gamma, dis(gen));
                        if (!available_new_infected) continue;
                        if (person->quarantine_status)
                            available_new_infected = std::min(max_in_quarantine - person->decendants,available_new_infected);
                        int new_infected = 0;
                        for (int ni = 0; ni < available_new_infected; ni++) {
                            // Check if the individual belongs to S, and
                            if ((idis(gen) < S) && (S > 0)) {
                                bool quarantine = (dis(gen) < percentage_in_quarantine[day]) ? true : false;
                                new_infected++;
                                S--;
                                population.new_individual(day, ind, true, Status::sick, quarantine);
                            }
                        }
                        person->decendants += new_infected;
                    } else {
                        person->active = false;
                        person->status = Status::recovered;
                        if (ind == population.first_individual()) population.move_first(ind);
                    }
                }
            }

            if (recont && (day != 0))
                if (percentage_in_quarantine[day - 1] != percentage_in_quarantine[day]) {
                    recontaminate(population, percentage_in_quarantine[day]);
                }

            int kp = 0, dp = 0;
            for (unsigned int ui = 0; ui < population.size(); ui++) {
                auto person = population[ui];
                if ((person->parent == -1) ||
                    (person->days_of_infection < max_transmission_day))
                    continue;
                kp++;
                dp += person->decendants;
            }
            if (kp)
                r_0_stat.add_value(day, double(dp) / kp);
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