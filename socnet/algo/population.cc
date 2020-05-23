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

void
Population::seed_infected(const std::vector<int>& i0active, const std::vector<int>& i0recovered, const double percentage)
{
    std::uniform_real_distribution<> dis(0.0, 1.0);
    bool quarantine;

    int doi = 0;
    for (auto &n : i0recovered) {
        for (int i = 0; i < n; i++) {
            quarantine = (dis(gen) < percentage) ? true : false;
            seed_individual(false, doi, Status::recovered, quarantine);
        }
        doi++;
    }

    doi = 0;
    for (auto& n : i0active) {
        for (int i = 0; i < n; i++) {
            quarantine = (dis(gen) < percentage) ? true : false;
            seed_individual(true, doi, Status::sick, quarantine);
        }
        doi++;
    }

    return;
}
