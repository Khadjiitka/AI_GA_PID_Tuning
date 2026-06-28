import os
import sys
import time
import json
import urllib.request
import numpy as np

# Setting up paths
current_file_dir = os.path.dirname(os.path.abspath(__file__)) 
project_root = os.path.abspath(os.path.join(current_file_dir, '..')) 

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database import init_db, save_experiment_result
from src.ga_optimizer import GeneticPIDOptimizer

def run_main_optimization():
    print("\n" + "="*60)
    print(" The PID-cascade optimization intelligence system has been launched")
    print("="*60)
    
    # Database initialization
    init_db()
    
    # Creating an optimizer (20 candidates, 15 generations of evolution)
    optimizer = GeneticPIDOptimizer(population_size=20, generations=15)
    
    # Starting the full AI training cycle in the delta-model simulator
    evolution_history = optimizer.run_optimization()
    
    # Let's pull out the winner of the evolution (the last generation, the best result)
    final_best_score, final_best_candidate = evolution_history[-1]
    
    print("\n" + "-"*40)
    print(" EVOLUTION COMPLETE! THE BEST PARAMETERS FOUND:")
    print(f"    Coefficient Kp: {final_best_candidate['kp']}")
    print(f"    Coefficient Ki: {final_best_candidate['ki']}")
    print(f"    Coefficient Kd: {final_best_candidate['kd']}")
    print(f"    Final Fitness Score: {final_best_score:.2f}")
    print("-"*40 + "\n")
    
    # Saving experiment results in an SQLite database
    for gen_idx, (score, candidate) in enumerate(evolution_history):
        save_experiment_result(
            kp=candidate['kp'],
            ki=candidate['ki'],
            kd=candidate['kd'],
            fitness_version="v2.0_simulation_ga",
            fitness_score=score,
            status="success" if score < 120.0 else "failed",
            csv_filename=f"ga_generation_{gen_idx+1}.csv"
        )
        
    print("All stages of evolution and the best chromosomes are successfully documented in the db experiments.db!")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_main_optimization()




    # Коли увімкнено режим stream
    #  run_pipeline(mode="stream")

    # для запуску коду ввести в терміналі python -m src.main