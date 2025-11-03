import random
import time
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
    
    def distance_to(self,other):
        """Compute Haversine distance in kilometers"""
        R = 6371                           # radius of earth to get distance in KM
        lat1,lon1 = math.radians(self.latitude),math.radians(self.longitude)
        lat2,lon2 = math.radians(other.latitude),math.radians(other.longitude)
        dlat,dlon = lat2 - lat1 , lon2-lon1
        a = math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
        return R * c
    def __repr__(self):
        return f"{self.name} : ({self.latitude},{self.longitude})"
    

# Class Graph to store the distance_matrix and pheromone_matrix \

class Graph:

    def __init__(self,cities):
        self.cities = cities
        self.num_cities = len(cities)
        self.distance_matrix = self.calculate_distance_matrix()
        self.pheromone_matrix = [[1.0 for _ in range(self.num_cities)] for _ in range(self.num_cities)]

    def calculate_distance_matrix(self):
        n = self.num_cities 
        matrix = [[0.0 for _ in range(n)]for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j :
                    matrix[i][j] = self.cities[i].distance_to(self.cities[j])
        return matrix
    
    def pheromenes(self,update_rate):
        for i in range(self.num_cities):
            for j in range(self.num_cities):
                self.pheromone_matrix[i][j] *= ( 1 - update_rate)

    def update_pheromene(self,path,concentration):
        for i in range(len(path) - 1):
            a, b = path[i], path[i+1]
            self.pheromone_matrix[a][b] += concentration
            self.pheromone_matrix[b][a] += concentration
    
    def get_distance(self,i,j):
        return self.distance_matrix[i][j]
    
    def get_pheromene(self,i,j):
        return self.pheromone_matrix[i][j]
    
# class Ant to calculate probabilities 

class Ant:
    
    def __init__(self,graph,alpha=1.0,beta=5.0):
        self.graph = graph
        self.alpha = alpha
        self.beta = beta
        self.num_cities = graph.num_cities
        self.reset()

    def reset(self):
        self.path = []
        self.total_distance = 0.0
        self.visited = [False]* self.num_cities
        self.current_city = random.randint(0,self.num_cities - 1)
        self.path.append(self.current_city)
        self.visited[self.current_city] = True 

    def probabilities(self):
        probabilities = []
        current = self.current_city
        for next_city in range(self.num_cities):
            if not self.visited[next_city]:
                pheromone = self.graph.get_pheromene(current,next_city) ** self.alpha
                distance = self.graph.get_distance(current,next_city)
                visibility = (1.0 / distance) ** self.beta if distance > 0 else 0
                probabilities.append((next_city,pheromone*visibility))
        total = sum(prob for _, prob in probabilities)
        return[(city,prob/total) for city,prob in probabilities] if total > 0 else []
    
    def choose_next_city(self):
        probs = self.probabilities()
        if not probs:
            return None
        r = random.random()
        cumulative = 0.0
        for city, prob in probs:
            cumulative += prob
            if r <= cumulative:
                return city
        return probs[-1][0]
    
    def move(self):
        next_city = self.choose_next_city()
        if next_city is not None:
            self.total_distance += self.graph.get_distance(self.current_city,next_city)
            self.current_city = next_city
            self.path.append(next_city)
            self.visited[next_city] = True
    
    def complete_path(self):
        while len(self.path) < self.num_cities:
            self.move()

        # return to start city 
        self.total_distance += self.graph.get_distance(self.path[-1],self.path[0])
        self.path.append(self.path[0])


# class ACO Implementation 

class ACO_TSP:

    def __init__(self,file_path):
        self.city_file = file_path
        self.cities = []
        self.read_cities(file_path)
        self.graph = Graph(self.cities)
    
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

    def run(self, num_ants=10, num_iteration=50, alpha=1.0, beta=5.0, update_rate=0.1):
        best_path = None
        best_distance = float('inf')

        for iter_num in range(num_iteration):
            ants = [Ant(self.graph, alpha, beta) for _ in range(num_ants)]
            iteration_best = float('inf')
            iteration_distances = []
            
            for ant in ants:
                ant.complete_path()
                iteration_distances.append(ant.total_distance)

                # Local best for this iteration
                if ant.total_distance < iteration_best:
                    iteration_best = ant.total_distance

                # Update global best
                if ant.total_distance < best_distance:
                    best_distance = ant.total_distance
                    best_path = ant.path

                
            self.graph.pheromenes(update_rate)   # Evaporate old pheromone
            for ant in ants:
                contribution = 1.0 / ant.total_distance
                self.graph.update_pheromene(ant.path, contribution)

    
            avg_distance = sum(iteration_distances) / len(iteration_distances)
            print(f"Iteration {iter_num + 1:03d}: "
              f"Best = {iteration_best:.2f} km, "
              f"Avg = {avg_distance:.2f} km, "
              f"Global Best = {best_distance:.2f} km")

        # --- Final results ---
        print("\nFinal Best Path:")
        for i in best_path:
            print(self.cities[i].name, end=" -> ")
        print(self.cities[best_path[0]].name)
        print(f"Total distance: {best_distance:.2f} km")

# main function

if __name__ == "__main__":

    aco = ACO_TSP("india_cities.txt")
    aco.run(num_ants=15,num_iteration=100,alpha=1.0,beta=5.0,update_rate=0.1)
                

                



    
