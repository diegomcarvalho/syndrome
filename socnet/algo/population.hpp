#ifndef POPULATION_HPP
#define POPULATION_HPP

#include <memory>
#include <random>
#include <vector>

enum class Status
{
    recovered,
    sick,
    severe,
    death
};

struct Individual
{
    int contamination_day;
    int parent;
    bool active;
    int days_of_infection;
    int decendants;
    Status status;
    bool quarantine_status;
    Individual(int c = 0,
               int p = -1,
               bool a = false,
               Status s = Status::recovered,
               bool q = false)
      : contamination_day(c)
      , parent(p)
      , active(a)
      , days_of_infection(0)
      , decendants(0)
      , status(s)
      , quarantine_status(q)
    {}
};

class Population
{
    std::mt19937_64 gen;
    int first_ind;
    // std::vector<std::shared_ptr<Individual>> population;
    std::vector<Individual*> population;

  public:
    Population(const int expected_size = 1000) { 
        population.reserve(expected_size);
        first_ind = 0;
    }
    ~Population() { reset_population(); }
    Individual* operator[](const int index) { return population[index]; }
    void new_individual(const int day, const int parent, const bool active, const Status st, const bool quarantine) {
        population.push_back(new Individual(day, parent, active, st, quarantine));
    }
    void reset_population();
    void seed_infected(const int i0active, const int i0recovered, const double percentage);
    unsigned int size() const { return population.size(); }
    int first_individual() const { return first_ind; }
    void move_first(const int id) { first_ind = id; }
};
#endif // POPULATION_HPP