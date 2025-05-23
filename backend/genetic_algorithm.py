import random
import math


class GeneticAlgorithm:
    def __init__(self, algo_data, route_data):
        self.pop_size = int(algo_data["popSize"])
        self.selection_type = algo_data["selectionType"]
        self.crossover = algo_data["crossover"]
        self.mutation = algo_data["mutation"]
        self.stop_condition = algo_data["stopCondition"]
        self.routes = route_data
        self.max_no_improvement = 5  # Max generations with no improvement
        self.best_fitness = float("inf")
        self.no_improvement_generations = 0
        self.max_gen = 10  # Example value for maximum generations

    def run(self):
        population = self.initialize_population()

        for generation in range(self.max_generations()):
            selected_parents = self.selection(population)
            offspring = self.crossover_population(selected_parents)
            self.mutate_population(offspring)
            population = self.create_new_population(offspring)

            best_in_generation = min(population, key=lambda x: x["fitness"])
            if best_in_generation["fitness"] < self.best_fitness:
                self.best_fitness = best_in_generation["fitness"]
            else:
                self.no_improvement_generations += 1

            if self.check_stop_condition(population):
                break
        unique_routes = self.get_unique_population(population)
        print(unique_routes[:3])
        return unique_routes[:3]

    def get_unique_population(self, population):
        unique_routes = []
        seen_routes = set()

        for individual in population:
            route_str = "".join([str(point["name"]) for point in individual["route"]])
            if route_str not in seen_routes:
                seen_routes.add(route_str)
                unique_routes.append(individual)

        return sorted(unique_routes, key=lambda x: x["fitness"])

    def initialize_population(self):
        # Find the start route and end route and all other routes
        start_point = [r for r in self.routes if r["isStart"] == 1][0]
        end_point = [r for r in self.routes if r["isEnd"] == 1][0]
        other_points = [r for r in self.routes if (r["isStart"] == 0 | r["isEnd"] == 0)]

        population = []

        for _ in range(self.pop_size):
            # Create a random permutation of other_points and avoid repetition
            random_permutation = random.sample(
                other_points,
                len(other_points),
            )

            individual = [start_point] + random_permutation + [end_point]

            # Calculate fitness for the individual
            individual_fitness = self.evaluate_fitness(individual)

            # Append the individual with its fitness to the population
            population.append({"route": individual, "fitness": individual_fitness})

        return population

    def evaluate_fitness(self, individual):
        distance = 0
        for i in range(len(individual) - 1):
            a = individual[i]["address"]
            b = individual[i + 1]["address"]
            distance += math.sqrt(
                (a["lat"] - b["lat"]) ** 2 + (a["lang"] - b["lang"]) ** 2
            )
        return distance

    def selection(self, population):
        if self.selection_type == "tournament":
            return self.tournament_selection(population)
        elif self.selection_type == "roulette":
            return self.roulette_selection(population)

    def tournament_selection(self, population, k=3):
        selected = []
        for _ in range(self.pop_size):
            tournament = random.sample(population, k)
            best_parent = min(tournament, key=lambda x: x["fitness"])
            selected.append(best_parent)
        return selected

    def roulette_selection(self, population):
        total_fitness = sum(1 / individual["fitness"] for individual in population)
        probabilities = [
            (1 / individual["fitness"]) / total_fitness for individual in population
        ]
        selected = random.choices(population, probabilities, k=self.pop_size)
        return selected

    def crossover_population(self, parents):
        offspring = []
        if not self.crossover:
            return parents

        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                parent1 = parents[i]["route"]
                parent2 = parents[i + 1]["route"]
                child1, child2 = self.order_crossover(parent1, parent2)
                if len(child1) < len(self.routes) or len(child2) < len(self.routes):
                    print("skipping individual")
                    continue
                offspring.append(
                    {"route": child1, "fitness": self.evaluate_fitness(child1)}
                )
                offspring.append(
                    {"route": child2, "fitness": self.evaluate_fitness(child2)}
                )

        return offspring

    def order_crossover(self, p_1, p_2):
        size = len(self.routes)

        def isStart(ind):
            return 0 if ind[0]["isStart"] else 1

        def isEnd(ind):
            return size if ind[size - 1]["isEnd"] else size - 1

        if self.crossover["type"] == "single":
            point = random.randint(1, size - 2)
            child1 = p_1[isStart(p_1) : point] + p_2[point : isEnd(p_1)]
            child2 = p_2[isStart(p_2) : point] + p_1[point : isEnd(p_2)]
        else:  # Multi-point crossover
            point1, point2 = sorted(random.sample(range(1, len(self.routes) - 1), 2))
            child1 = (
                p_1[isStart(p_1) : point1]
                + p_2[point1:point2]
                + p_1[point2 : isEnd(p_1)]
            )
            child2 = (
                p_2[isStart(p_2) : point1]
                + p_1[point1:point2]
                + p_2[point2 : isEnd(p_2)]
            )
        for i in range(size):
            if i > len(child1):
                for gene in p_2:
                    if gene not in child1:
                        child1[i] = gene
                        break
            if i > len(child2):
                for gene in p_1:
                    if gene not in child2:
                        child2[i] = gene
                        break

        return child1, child2

    def mutate_population(self, population):
        if not self.mutation:
            return

        mutation_rate = int(self.mutation["rate"])
        for individual in population:
            if random.random() < mutation_rate:
                idx1, idx2 = random.sample(range(len(self.routes)), 2)
                individual["route"][idx1], individual["route"][idx2] = (
                    individual["route"][idx2],
                    individual["route"][idx1],
                )
        return population

    def create_new_population(self, offspring):
        # Elitism: Keep the best individuals from the current generation
        num_elites = int(self.pop_size * 0.1)  # Keep top 10% as elites

        for individual in offspring:
            individual["fitness"] = self.evaluate_fitness(individual["route"])
        # Ensure num_elites is at least 1
        num_elites = max(1, int(self.pop_size * 0.1))

        # Debug: Print the size of offspring and num_elites
        print(f"Offspring size: {len(offspring)}, num_elites: {num_elites}")

        # Elitism: Keep the best individuals from the current generation
        current_best = sorted(offspring, key=lambda x: x["fitness"])[:num_elites]

        # Debug: Print current_best to verify its contents
        print(f"Current best (elite individuals): {current_best}")

        unique_offspring = []
        new_population = []

        for individual in offspring:
            route_tuple = individual["route"]

            if route_tuple not in unique_offspring:
                unique_offspring.append(route_tuple)
                new_population.append(individual)

        # Ensure the new population size matches the original population size
        if not current_best:
            return
        while len(new_population) < self.pop_size:
            additional_individual = random.choice(
                current_best
            )  # Add more from elites if needed
            new_population.append(additional_individual)

        # Sort by fitness and return
        return sorted(new_population, key=lambda x: x["fitness"])

    def check_stop_condition(self, population):
        if self.stop_condition == "maxGeneration":
            return len(population) >= self.max_gen
        elif self.stop_condition == "noImprovement":
            return self.no_improvement_generations >= self.max_no_improvement
        elif self.stop_condition == "satisfactorySolution":
            # Logic to check for a satisfactory solution
            return False  # Placeholder

    def max_generations(self):
        return self.max_gen


# Example integration for drawing on a map and generating graphs
def draw_route_on_map(route_names):
    # Placeholder function to integrate with Google Maps API to draw the route
    pass


def generate_graphs(route_data):
    # Placeholder function to generate graphs for fuel consumption, fuel cost, and travel time
    pass


# def main():
#     algo_data = {
#         "popSize": "9",
#         "selectionType": "tournament",
#         "crossover": {"type": "single", "rate": 0.8},
#         "mutation": {"types": ["cityChange"], "rate": 0.1},
#         "stopCondition": "noImprovement",
#     }

#     route_data = [
#         {
#             "name": "aa",
#             "isStart": 0,
#             "isEnd": 0,
#             "address": {"lat": 51.51109290500474, "lang": -0.11715888977050781},
#         },
#         {
#             "name": "ab",
#             "isStart": 0,
#             "isEnd": 1,
#             "address": {"lat": 55.51109290500474, "lang": -0.11555588977050781},
#         },
#         {
#             "name": "ac",
#             "isStart": 0,
#             "isEnd": 0,
#             "address": {"lat": 53.51109290500474, "lang": -0.11526888977050781},
#         },
#         {
#             "name": "bb",
#             "isStart": 1,
#             "isEnd": 0,
#             "address": {"lat": 51.508945878220516, "lang": -0.13951454787254125},
#         },
#         {
#             "name": "cc",
#             "isStart": 0,
#             "isEnd": 0,
#             "address": {"lat": 51.51353979852902, "lang": -0.14183197646140844},
#         },
#     ]

#     ga = GeneticAlgorithm(algo_data, route_data)
#     best_routes = ga.run()

#     # Display the best routes found
#     for idx, route in enumerate(best_routes):
#         route_names = [point["name"] for point in route["route"]]
#         print(f"Route {idx+1}: {route_names} with Fitness: {route['fitness']}")
#     generate_graphs(best_routes)


# if __name__ == "__main__":
#     main()
