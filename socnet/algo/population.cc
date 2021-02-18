#include "population.hpp"

void
Population::reset_population()
{

    //for (unsigned int ui = 0; ui < population.size(); ui++)
    //    delete population[ui];
    population.clear();

    return;
}

void
Population::seed_infected(const int i0active, const int i0recovered, const double percentage)
{
    std::uniform_real_distribution<> dis(0.0, 1.0);

    for (int i = 0; i < i0recovered; i++) {
        new_subject(0, -1, 0, false, (dis(my_gen) < percentage));
    }

    

    for (int i = 0; i < i0active; i++) {
        new_subject(0, -1, 0, true, (dis(my_gen) < percentage));
    }

    this->first_ind = i0recovered;

    return;
}

void
Population::seed_infected(const std::vector<int>& i0active, const std::vector<int>& i0recovered, const double percentage)
{
    std::uniform_real_distribution<> dis(0.0, 1.0);

    for (auto &n : i0recovered) {
        for (int i = 0; i < n; i++) {
            seed_subject(false, (dis(my_gen) < percentage));
        }
    }

    for (auto& n : i0active) {
        for (int i = 0; i < n; i++) {
			seed_subject(true, (dis(my_gen) < percentage));
        }
    }
    
    this->first_ind = i0recovered.size();

    return;
}
