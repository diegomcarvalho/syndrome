#include "population.hpp"


void
Population::reset_population()
{
    for (unsigned int ui = 0; ui < population.size(); ui++)
        delete population[ui];
    population.clear();

    return;
}

void
Population::seed_infected(const int i0active, const int i0recovered, const double percentage)
{
    std::uniform_real_distribution<> dis(0.0, 1.0);
    bool quarantine;

    for (int i = 0; i < i0recovered; i++) {
        quarantine = (dis(gen) < percentage) ? true : false;
        new_individual(0, -1, false, Status::recovered, quarantine);
    }

    for (int i = 0; i < i0active; i++) {
        quarantine = (dis(gen) < percentage) ? true : false;
        new_individual(0, -1, true, Status::sick, quarantine);
    }

    return;
}
