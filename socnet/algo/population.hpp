#ifndef POPULATION_HPP
#define POPULATION_HPP

#include <memory>
#include <random>
#include <vector>


const uint8_t fACTIVE = 0x01;
const uint8_t fQUARANTINE = 0x01 << 1;

class Subject
{
  private:
  public:
    uint8_t flags;
    uint8_t days_of_infection;
    uint32_t parent;
    uint16_t contamination_day;
    uint8_t decendants;

    inline const bool is_active() { return this->flags & fACTIVE; }
    inline void set_active() { this->flags ^= fACTIVE; }
    inline void clear_active() { this->flags &= ~fACTIVE; }
    inline const bool is_quarantined() { return this->flags & fQUARANTINE; }
    inline void set_quarantined() { this->flags ^= fQUARANTINE; }
    inline void clear_quarantined() { this->flags &= ~fQUARANTINE; }
	inline void set_active_and_quarantine( bool a, bool q  ) { this->flags = uint8_t(a) | (uint8_t(q) << 1); }
    Subject(const int doi = 0,
			const int p = -1,
			const int c = 0,
			const bool a = false,
			const bool q = false)
      : days_of_infection(doi)
      , parent(p)
      , contamination_day(c)
	  , decendants(0)
    {
        this->flags = uint8_t(a) | (uint8_t(q) << 1);
    }
    Subject(const bool a, const bool q)
      : days_of_infection(0)
      , parent(-1)
      , contamination_day(0)
	  , decendants(0)
    {
        this->flags = uint8_t(a) | (uint8_t(q) << 1);
    }
};

class Population
{
    std::mt19937_64 my_gen;
    int first_ind;
    std::vector<Subject> population;

  public:
    Population(const int expected_size = 1000) { 
        population.reserve(expected_size);
        first_ind = 0;
    }
    ~Population() { reset_population(); }
    Subject& operator[](const int index) { return population[index]; }
    void new_subject(const int day, const int parent, const int cDay, const bool active, const bool quarantine) {
        population.push_back(Subject(day, parent, cDay, active, quarantine));
    }
    void seed_subject(const bool active, const bool quarantine) {
        population.push_back(Subject(active, quarantine));

    }
    void reset_population();
    void seed_infected(const int i0active, const int i0recovered, const double percentage);
    void seed_infected(const std::vector<int>& i0active, const std::vector<int>& i0recovered, const double percentage);
    unsigned int size() const { return population.size(); }
    int first_subject() const { return first_ind; }
    void move_first(const int id) { first_ind = id; }
};

#endif // POPULATION_HPP