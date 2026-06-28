import numpy as np
import random
from src.metrics import evaluate_flight_fitness

class GeneticPIDOptimizer:
    def __init__(self, population_size=20, generations=15, mutation_rate=0.15, dt=0.02):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.dt = dt
        
        # PID coefficient search boundaries
        self.bounds = {
            'kp': (0.1, 4.5),
            'ki': (0.0, 1.5),
            'kd': (0.0, 2.0)
        }

    def init_population(self):
        """  Generating the initial random population of PID candidates. """
        population = []
        for _ in range(self.population_size):
            candidate = {
                'kp': round(random.uniform(*self.bounds['kp']), 3),
                'ki': round(random.uniform(*self.bounds['ki']), 3),
                'kd': round(random.uniform(*self.bounds['kd']), 3)
            }
            population.append(candidate)
        return population

    def simulate_candidate(self, candidate, steps=150):
        Kp, Ki, Kd = candidate['kp'], candidate['ki'], candidate['kd']
        
        pitch = 7.0  # starting the test with the maximum standard deviation of 7 degrees
        gyro_y = 0.0  
        
        pitch_history = []
        gyro_history = []
        
        integral_error = 0
        last_error = 0
        
        for _ in range(steps):
            error = 0.0 - pitch  # Target — steady horizon (0 degrees)
            
            # Calculation of the basic PID signal
            p_term = Kp * error
            integral_error += error * self.dt
            i_term = Ki * integral_error
            d_term = Kd * (error - last_error) / self.dt
            last_error = error
            
            # Basic PID control
            U_pid = p_term + i_term + d_term
            
        
            # We adjust the control to shift relative to the average thrust (for example 1200)
            motor_signal = 1200 + (U_pid * 100) 
            motor_signal = max(600, min(1800, motor_signal)) 
            
            # Physical response of the delta model to the actual motor signal
            virtual_thrust = (motor_signal - 1200) / 600.0
            gyro_y += (virtual_thrust * 15.0 - gyro_y * 0.15) * self.dt
            pitch += gyro_y * self.dt
            
            # Check for a critical angle of 10 degrees (Death of the individual)
            if abs(pitch) >= 10.0:
                # The individual immediately stops the test due to an accident
                pitch_history.append(pitch)
                gyro_history.append(gyro_y)
                break  
                
            pitch_history.append(pitch)
            gyro_history.append(gyro_y)
          
        return pitch_history, gyro_history

    def evaluate_population(self, population):
        """ Running the whole population through the simulator and calculating the Fitness Score for each one."""
        scored_population = []
        for candidate in population:
            pitch_hist, gyro_hist = self.simulate_candidate(candidate)
            # Calculating the overall fitness (penalty integral + Overshoot + Settling Time)
            score = evaluate_flight_fitness(pitch_hist, gyro_hist, dt=self.dt)
            scored_population.append((score, candidate))
            
        # We sort: the LESS fitness (mistake), the BETTER the candidate
        scored_population.sort(key=lambda x: x[0])
        return scored_population

    def selection(self, scored_population):
        """Tournament selection (choosing the best parents for breeding)."""
        # Elitism: we strictly take the 2 best chromosomes without any changes
        selected = [scored_population[0][1], scored_population[1][1]]
        
        # We pick the rest through a tournament of random pairs
        while len(selected) < self.population_size:
            player1 = random.choice(scored_population)[1]
            player2 = random.choice(scored_population)[1]
            
            # The one who scored fewer penalty points in the simulator won.
            score1 = evaluate_flight_fitness(*self.simulate_candidate(player1))
            score2 = evaluate_flight_fitness(*self.simulate_candidate(player2))
            
            selected.append(player1 if score1 < score2 else player2)
            
        return selected

    def crossover(self, parent1, parent2):
        """ Arithmetic crossover."""
        alpha = random.uniform(0.1, 0.9)
        child = {}
        for param in ['kp', 'ki', 'kd']:
            # Наследуем свойства обоих родителей
            value = alpha * parent1[param] + (1 - alpha) * parent2[param]
            child[param] = round(value, 3)
        return child

    def mutate(self, candidate):
        """ Mutation: a random change of one of the coefficients to get out of local minima. """
        mutated = candidate.copy()
        for param in ['kp', 'ki', 'kd']:
            if random.random() < self.mutation_rate:
                # Adding a small random normal deviation
                mutation_value = random.normalvariate(0, 0.2)
                new_value = mutated[param] + mutation_value
                low, high = self.bounds[param]
                mutated[param] = round(max(low, min(high, new_value)), 3)
        return mutated

    def run_optimization(self):
        """ The main loop of the AI optimizer's evolution. """
        print(f" Starting GA evolution: {self.generations} generations, population {self.population_size}")
        
        population = self.init_population()
        history = []
        
        for gen in range(1, self.generations + 1):
            scored_pop = self.evaluate_population(population)
            best_score, best_candidate = scored_pop[0]
            
            print(f"Generation {gen:02d} | Best Fitness: {best_score:.2f} | PID: Kp={best_candidate['kp']}, Ki={best_candidate['ki']}, Kd={best_candidate['kd']}")
            history.append((best_score, best_candidate))
            
            # Parent selection
            selected_parents = self.selection(scored_pop)
            
            # Creating the next generation (Crossover + Mutation)
            next_generation = [scored_pop[0][1], scored_pop[1][1]]  # Preserving the elite
            
            while len(next_generation) < self.population_size:
                p1 = random.choice(selected_parents)
                p2 = random.choice(selected_parents)
                child = self.crossover(p1, p2)
                child = self.mutate(child)
                next_generation.append(child)
                
            population = next_generation
            
        return history