import numpy as np

def normalize_data(pitch, gyro_y, pitch_limit=10.0, gyro_limit=250.0):
    """ Converting quantities to a dimensionless form """
    pitch_norm = pitch / pitch_limit
    gyro_norm = gyro_y / gyro_limit
    return pitch_norm, gyro_norm

def calculate_instantaneous_cost(pitch_norm, gyro_norm, w_theta=0.7, w_omega=0.3):
    """ S(k) = w_theta * |theta_norm| + w_omega * |gyro_norm| """
    return w_theta * abs(pitch_norm) + w_omega * abs(gyro_norm)

def evaluate_flight_fitness(pitch_history, gyro_history, dt=0.02):
    CRITICAL_PITCH = 10.0  
    CRITICAL_GYRO = 250.0  
    
    
    if len(pitch_history) == 0 or abs(pitch_history[-1]) >= CRITICAL_PITCH:
        return 99999.0  
        
    total_fitness = 0
    
    # Calculation of the integral penalty for live specimens ...
    for pitch, gyro in zip(pitch_history, gyro_history):
        # Use the normalization function
        pitch_norm, gyro_norm = normalize_data(pitch, gyro, CRITICAL_PITCH, CRITICAL_GYRO)
        
        # We calculate the instantaneous value of state S(k)
        s_k = calculate_instantaneous_cost(pitch_norm, gyro_norm)
        total_fitness += s_k * dt
        
    # Extra fine for exceeding the comfort zone by 7 degrees (Overshoot)
    max_pitch = max(abs(p) for p in pitch_history)
    if max_pitch > 7.0:
        total_fitness += (max_pitch - 7.0) * 15.0
        
    return round(total_fitness, 2)