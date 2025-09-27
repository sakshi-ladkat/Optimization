import random
import math
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


# City Class to store City info 
class City:
    def __init__(self,name,latitude,longitude):
        self.name = name
        self.latitude = round(latitude,2)
        self.longitude = round(longitude,2)

    def coords(self):
        return [self.longitude,self.latitude]
    

# Parent Class : a generation 
class Parent:
    def __init__(self,cities,population_size=200):

        # cities : list of City objects
        #population_size : how many individuals in the generation

        self.cities = cities
        self.population_size = population_size
        self.population = self.generate_random_paths(population_size)

    def distance(self,city_a,city_b):
        return math.sqrt((city_a.longitude - city_b.longitude)**2 + 
                         (city_a.latitude - city_b.latitude)**2)
    
    def total_distance(self, path):

        # Total round - trip distace for a path (list of indices). 

        total = 0.0
        n = len(path)
        if n == 0:
            return 0.0
        for i in range(len(path)):
            a = self.cities[path[i-1]].coords()  
            b = self.cities[path[i]].coords()   
            total += math.dist(a, b)
        return total


    def generate_random_paths(self,total_destinations):

        # Creates initial random population of permutations (start city fixed as 0 )

        random_paths = []
        n = len(self.cities)
        if n == 0:
            return random_paths
        
        for _ in range(self.population_size):
            random_path = list(range(1,n))
            random.shuffle(random_path)
            random_path = [0] + random_path
            random_paths.append(random_path)
        return random_paths
    
    def choose_survivors(self,old_generation,top_n=100):
        if not old_generation:
            return []
        generation = old_generation[:]
        random.shuffle(old_generation)
        midway = len(old_generation)//2
        survivors = []
        for i in range(midway):
            if self.total_distance(generation[i]) < self.total_distance(generation[i+midway]):
                survivors.append(generation[i])
            else:
                survivors.append(generation[i+midway])

        if len(survivors) > top_n:
            survivors = sorted(survivors,key = lambda p:self.total_distance(p))[:top_n]
        return survivors

# child class : new generation from parents

class Child(Parent):

    def __init__(self,parent_population,top_n=120,mutation_rate=0.01):
        super().__init__(parent_population.cities,parent_population.population_size)
        self.survivors = parent_population.choose_survivors(parent_population.population,top_n=top_n)
        if not self.survivors:
            self.survivors = parent_population.population[:max(1,top_n)]
        self.population = self.generate_new_population(mutation_rate= mutation_rate)

    def create_offspring(self,parent_a,parent_b):
        offspring = []
        length = len(parent_a)
        if length <=1:
            return parent_a[:]
        start = random.randint(0,length-1)
        finish = random.randint(start,length)
        sub_path_from_a = parent_a[start:finish]
        remaining_path_from_b = list([item for item in parent_b if item not in sub_path_from_a])
        rem_idx = 0
        for i in range(length):
            if start <= i < finish:
                offspring.append(sub_path_from_a[i-start])
            else:
                offspring.append(remaining_path_from_b[rem_idx])
                rem_idx += 1
        return offspring

    def apply_crossover(self,survivors):
        offsprings = []
        if len(survivors) < 2:
            return survivors[:]
        
        if len(survivors)%2 == 1:
            survivors = survivors[:-1]
        midway = len(survivors)//2
        for i in range(midway):
            parent_a,parent_b = survivors[i],survivors[i+midway]
            offsprings.append(self.create_offspring(parent_a,parent_b))
            offsprings.append(self.create_offspring(parent_b,parent_a))

        while len(offsprings) < self.population_size:
            s = random.choice(survivors)
            child = s[:]

            if len(child) > 2:
                i, j = random.sample(range(1,len(child)),2)
                child[i],child[j] = child[j],child[i]
            offsprings.append(child)
        return offsprings[:self.population_size]

    def apply_mutations(self,generation,mutation_rate):
        gen_wt_mutations =[]
        for path in generation:
            new_path = path[:]
            if random.random() < mutation_rate:
                index1,index2 = random.sample(range(1,len(new_path)),2)
                new_path[index1],new_path[index2] = new_path[index2],new_path[index1]
            gen_wt_mutations.append(new_path)
        return gen_wt_mutations
    
    def generate_new_population(self,mutation_rate=0.01):
        crossover = self.apply_crossover(self.survivors)
        new_population = self.apply_mutations(crossover,mutation_rate)
        self.population = new_population
        return new_population

# Travelling salesman problem Genetic Algorithm
class Genetic_TSP:

    def __init__(self,city_file):
        self.city_file = city_file
        self.cities = []
        self.read_cities(city_file)

    def read_cities(self,city_file):
        geolocator = Nominatim(user_agent="Sakshi_APP")
        with open(city_file,"r",encoding="utf-8") as f:
            for idx , line in enumerate(f):
                city_name = line.strip()
                if not city_name:
                    continue
                try:
                    location = geolocator.geocode(f"{city_name},India",timeout=10)
                except (GeocoderTimedOut,GeocoderServiceError):
                    print(f"Geocoding error for '{city_name}',skipping")
                    continue
                if location is None:
                    print(f"City '{city_name}'not found! ")
                    continue
                c = City(city_name,location.latitude,location.longitude)
                self.cities.append(c)
                print(f"City[{idx:2d}]={c.name}({c.longitude:.2f},{c.latitude:.2f})")

    def run(self,generations,population_size,top_n,mutation_rate,patience):
        if len(self.cities) < 2:
            raise ValueError("Need at least 2 cities to run Genetic_TSP")
        
        parent = Parent(self.cities,population_size)
        best_path = min(parent.population,key=parent.total_distance)
        best_disatance = parent.total_distance(best_path)
        no_improve = 0

        print(f"Initial best distance:{best_disatance:.4f}")

        for gen in range(1,generations + 1):
            child = Child(parent,top_n=top_n,mutation_rate=mutation_rate)
            parent.population = child.population

            current_best_path = min(parent.population,key =parent.total_distance)
            current_path_distance = parent.total_distance(current_best_path)
            print(f"Generation{gen}:Best Distance = {current_path_distance:.4f}")

            if current_path_distance < best_disatance:
                best_disatance = current_path_distance
                best_path = current_best_path[:]

                no_improve = 0
            
            else:
                no_improve += 1

            if no_improve >= patience:
                print("\nStopping early at generation {gen}(no improvemment in {ptience} generations).")
       
        return best_path , best_disatance
    
if __name__ == "__main__":
        FILE = "india_cities.txt"
        ga = Genetic_TSP(FILE)
        best_path , best_distance = ga.run(generations=200,population_size=200,top_n=120,mutation_rate=0.01,patience=50)

        print("\nFinal Best Distance:",best_distance)
        print("Best Path(indices):",best_path)
        print("Best path (city names):",[ga.cities[i].name for i in best_path ]) 




   









