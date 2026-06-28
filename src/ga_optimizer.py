import numpy as np
import random
from src.metrics import evaluate_flight_fitness

class GeneticPIDOptimizer:
    def __init__(self, population_size=20, generations=15, mutation_rate=0.15, dt=0.02):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.dt = dt
        
        # Границы поиска коэффициентов PID согласно ТЗ и физическим лимитам стенда
        self.bounds = {
            'kp': (0.1, 4.5),
            'ki': (0.0, 1.5),
            'kd': (0.0, 2.0)
        }

    def init_population(self):
        """
        Генерация начальной случайной популяции PID-кандидатов.
        """
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
        """
        Экспериментальная дельта-модель изменения состояния (ΔU -> Δω -> Δθ).
        Симулирует поведение виртуального дрона на стенде с конкретным набором PID.
        """
        Kp, Ki, Kd = candidate['kp'], candidate['ki'], candidate['kd']
        
        pitch = 15.0  # Начальное отклонение стенда (дрон наклонен на 15 градусов)
        gyro_y = 0.0  # Начальная угловая скорость
        
        pitch_history = []
        gyro_history = []
        
        integral_error = 0
        last_error = 0
        
        for _ in range(steps):
            error = 0.0 - pitch  # Горизонт — наша цель
            
            # Расчет управляющего воздействия PID
            p_term = Kp * error
            integral_error += error * self.dt
            i_term = Ki * integral_error
            d_term = Kd * (error - last_error) / self.dt
            last_error = error
            
            U_pid = p_term + i_term + d_term
            
            # Физический шаг дельта-модели (переходные приращения)
            gyro_y += (U_pid * 15.0 - gyro_y * 0.15) * self.dt
            pitch += gyro_y * self.dt
            
            pitch_history.append(pitch)
            gyro_history.append(gyro_y)
            
        return pitch_history, gyro_history

    def evaluate_population(self, population):
        """
        Прогон всей популяции через симулятор и расчет Fitness Score для каждого.
        """
        scored_population = []
        for candidate in population:
            pitch_hist, gyro_hist = self.simulate_candidate(candidate)
            # Вычисляем комплексный фитнес (интеграл штрафов + Overshoot + Settling Time)
            score = evaluate_flight_fitness(pitch_hist, gyro_hist, dt=self.dt)
            scored_population.append((score, candidate))
            
        # Сортируем: чем МЕНЬШЕ фитнес (ошибка), тем ЛУЧШЕ кандидат
        scored_population.sort(key=lambda x: x[0])
        return scored_population

    def selection(self, scored_population):
        """
        Турнирная селекция (отбор лучших родителей для скрещивания).
        """
        # Элитизм: железно забираем 2 лучших хромосомы без изменений
        selected = [scored_population[0][1], scored_population[1][1]]
        
        # Остальных выбираем турниром из случайных пар
        while len(selected) < self.population_size:
            player1 = random.choice(scored_population)[1]
            player2 = random.choice(scored_population)[1]
            
            # Кто набрал меньше штрафных баллов в симуляторе — тот и победил
            score1 = evaluate_flight_fitness(*self.simulate_candidate(player1))
            score2 = evaluate_flight_fitness(*self.simulate_candidate(player2))
            
            selected.append(player1 if score1 < score2 else player2)
            
        return selected

    def crossover(self, parent1, parent2):
        """
        Арифметическое скрещивание (создание ребенка как взвешенной комбинации родителей).
        """
        alpha = random.uniform(0.1, 0.9)
        child = {}
        for param in ['kp', 'ki', 'kd']:
            # Наследуем свойства обоих родителей
            value = alpha * parent1[param] + (1 - alpha) * parent2[param]
            child[param] = round(value, 3)
        return child

    def mutate(self, candidate):
        """
        Мутация: случайное изменение одного из коэффициентов для выхода из локальных минимумов.
        """
        mutated = candidate.copy()
        for param in ['kp', 'ki', 'kd']:
            if random.random() < self.mutation_rate:
                # Добавляем небольшое случайное нормальное отклонение
                mutation_value = random.normalvariate(0, 0.2)
                new_value = mutated[param] + mutation_value
                # Проверяем, чтобы не выйти за границы ТЗ
                low, high = self.bounds[param]
                mutated[param] = round(max(low, min(high, new_value)), 3)
        return mutated

    def run_optimization(self):
        """
        Главный цикл эволюции ШИ-оптимизатора.
        """
        print(f" Запуск эволюции ГА: {self.generations} поколений, популяция {self.population_size}")
        
        population = self.init_population()
        history = []
        
        for gen in range(1, self.generations + 1):
            scored_pop = self.evaluate_population(population)
            best_score, best_candidate = scored_pop[0]
            
            print(f"Поколение {gen:02d} | Лучший Fitness: {best_score:.2f} | PID: Kp={best_candidate['kp']}, Ki={best_candidate['ki']}, Kd={best_candidate['kd']}")
            history.append((best_score, best_candidate))
            
            # Селекция родителей
            selected_parents = self.selection(scored_pop)
            
            # Создание следующего поколения (Скрещивание + Мутация)
            next_generation = [scored_pop[0][1], scored_pop[1][1]]  # Сохраняем элиту
            
            while len(next_generation) < self.population_size:
                p1 = random.choice(selected_parents)
                p2 = random.choice(selected_parents)
                child = self.crossover(p1, p2)
                child = self.mutate(child)
                next_generation.append(child)
                
            population = next_generation
            
        return history