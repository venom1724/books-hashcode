import math

def get_neighbourhood_function(rng):

    def neighbourhood_function(ranking):
        new_ranking = ranking[:]
        old_position = rng.randrange(len(ranking))
        if old_position==len(ranking)-1:
            old_position-=1
        new_position=old_position+1
        new_ranking[old_position], new_ranking[new_position] = new_ranking[new_position], new_ranking[old_position]
        return new_ranking, old_position, new_position

    def neighbourhood_function2(ranking):
        new_ranking = ranking[:]
        [old_position, new_position] = rng.sample(range(len(ranking)), 2)

        are_adjacent = abs(old_position - new_position) == 1

        available_positions = [x for x in range(len(ranking)) if x != old_position] if are_adjacent else None

        while are_adjacent and rng.random() < 0.5:
            new_position = rng.choice(available_positions)
            are_adjacent = abs(old_position - new_position) == 1

        new_ranking.insert(new_position, new_ranking.pop(old_position))

        return new_ranking, old_position, new_position

    return neighbourhood_function2

def get_multiplicative_cooling_schedule_function(cooling_ratio_multiplier):
    """ Returns a cooling schedule function of the form f(T) = a*T, "a" being the cooling ratio multiplier - a real
    number between 0 and 1 (As specified in the proforma)

    :param cooling_ratio_multiplier: real number a, 0 <= a <= 1
    :return: pointer to the cooling schedule function
    """
    if cooling_ratio_multiplier < 0 or cooling_ratio_multiplier > 1:
        raise Exception("The value for the cooling ration multiplier 'a' must be 0 <= a <= 1")

    def cooling_schedule(temperature):
        return cooling_ratio_multiplier * temperature
    return cooling_schedule


class SimulatedAnnealingWithNonImproveStoppingCriterion:
    """ Generic implementation of simulated annealing with the stopping criterion: stop after inspecting a
    num_non_improve of solutions without finding a new best solution

    The neighbourhood function, cost function, initial temperature, temperature length, cooling schedule function
    and num_non_improve (for the stopping criterion) are specified by the user

    rng: Object, instance of the "Random" class - random number generator that SA uses for determining the
    probability of moving uphill

    neighbourhood_function: pointer to a function - neighbourhood function, preferably using the same RNG (rng).
    The result of the function must be a tuple, whose first element is the neighbouring solution

    cost_function: pointer to a function - cost function, supporting calculating the cost of initial as well as
    neighbouring solutions

    initial_temperature: real number - initial temperature TI
    temperature_length: integer - temperature length TL

    cooling_schedule_function: pointer to a function - cooling schedule f()

    num_non_improve: integer - stopping criterion
    """
    def __init__(
            self,
            rng,
            neighbourhood_function,
            cost_function,
            initial_temperature,
            temperature_length,
            cooling_schedule_function,
            num_non_improve,
            better_solution_function,
    ):
        self.rng = rng
        self.neighbourhood_function = neighbourhood_function
        self.cost_function = cost_function
        self.initial_temperature = initial_temperature
        self.temperature_length = temperature_length
        self.cooling_schedule_function = cooling_schedule_function
        self.num_non_improve = num_non_improve
        self.better_solution_function = better_solution_function

    def run(self, initial_solution):
        number_of_uphill_moves = 0
        iterations_since_last_improvement = 0

        temperature = self.initial_temperature
        current_solution = initial_solution[:]
        # calculate the cost of the initial solution
        current_solution_cost = self.cost_function(initial_solution)

        # take the best solution to be the initial solution
        best_solution = current_solution[:]
        best_solution_cost = current_solution_cost

        # Continue the process until iterations_since_last_improvement is equal to num_non_improve
        while iterations_since_last_improvement < self.num_non_improve:
            # stay at a temperature T for TL iterations
            for _ in range(self.temperature_length):
                # get the neighbour of a solution produced by the neighbourhood function.
                neighbour = self.neighbourhood_function(current_solution)
                [neighbour_solution, rest] = neighbour[0], neighbour[1:]

                # calculate the cost of the neighbouring solution by using the cost function
                neighbour_solution_cost = self.cost_function(neighbour_solution)
                delta_cost = neighbour_solution_cost - current_solution_cost

                # if better than the current solution
                # accept the neighbouring solution as the current solution
                if delta_cost >= 0:
                    current_solution = neighbour_solution[:]
                    current_solution_cost = neighbour_solution_cost

                    # if better than best solution
                    # accept the neighbouring solution as the best solution and reset the number of iterations
                    # without improvement
                    # otherwise, increment the number of iterations without improvement by 1
                    if current_solution_cost > best_solution_cost:
                        self.better_solution_function(current_solution_cost,current_solution)
                        best_solution = current_solution[:]
                        best_solution_cost = current_solution_cost
                        iterations_since_last_improvement = 0
                    else:
                        iterations_since_last_improvement += 1

                # if worse than the current solution
                # accept it with probability p = e^(-deltaCost / T). If accepted, record that an uphill move occurred.
                # Always increment the number of iterations without improvement by 1
                else:
                    p = math.exp(delta_cost / temperature)
                    if self.rng.random() < p:
                        current_solution = neighbour_solution[:]
                        current_solution_cost = neighbour_solution_cost

                        number_of_uphill_moves += 1

                    iterations_since_last_improvement += 1

                if iterations_since_last_improvement >= self.num_non_improve:
                    break

            # after spending TL iterations at temperature T, invoke the cooling_schedule function to obtain the next
            # temperature T'
            temperature = self.cooling_schedule_function(temperature)

        return best_solution, best_solution_cost, number_of_uphill_moves
