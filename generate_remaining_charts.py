import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Connecting the project modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import metrics

os.makedirs('reports/figures', exist_ok=True)
plt.rcParams['font.family'] = 'DejaVu Sans'

# Running a simulation of the delta model
def simulate_delta_model(Kp, Ki, Kd, steps=150, dt=0.02):
    pitch = 15.0
    gyro_y = 0.0
    pitch_history, gyro_history = [], []
    integral_error, last_error = 0, 0
    
    for _ in range(steps):
        error = 0.0 - pitch
        p_term = Kp * error
        integral_error += error * dt
        i_term = Ki * integral_error
        d_term = Kd * (error - last_error) / dt
        last_error = error
        
        U_pid = p_term + i_term + d_term
        gyro_y += (U_pid * 15.0 - gyro_y * 0.15) * dt
        pitch += gyro_y * dt
        
        pitch_history.append(pitch)
        gyro_history.append(gyro_y)
        
    return pitch_history, gyro_history

# Getting data for bad and good regulators
pitch_bad, gyro_bad = simulate_delta_model(Kp=0.25, Ki=0.02, Kd=0.01)
pitch_good, gyro_good = simulate_delta_model(Kp=1.65, Ki=0.15, Kd=0.18)

time_axis = np.arange(150) * 0.02

# We calculate the dynamics of the change in the instantaneous value S(k) for both cases
s_k_bad = [metrics.calculate_instantaneous_cost(*metrics.normalize_data(p, g)) for p, g in zip(pitch_bad, gyro_bad)]
s_k_good = [metrics.calculate_instantaneous_cost(*metrics.normalize_data(p, g)) for p, g in zip(pitch_good, gyro_good)]


# ========================================================
# CHART 3: Transient process of angular velocity (Gyro Y)
# ========================================================
plt.figure(figsize=(10, 5))
plt.plot(time_axis, gyro_bad, color='orange', linestyle='--', label='Initial PID (High angular velocity)', linewidth=2)
plt.plot(time_axis, gyro_good, color='blue', label='Optimized AI PID (Stable Damping)', linewidth=2.5)
plt.axhline(0, color='black', linestyle=':', alpha=0.5)
plt.title('Dynamics of angular velocity change (Gyro Y) over time', fontsize=14, fontweight='bold')
plt.xlabel('Time (seconds)', fontsize=12)
plt.ylabel('Angular velocity Pitch Rate (deg/sec)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=11)
plt.savefig('reports/figures/03_gyro_response.png', dpi=300)
plt.savefig('03_gyro_response.png', dpi=300)
plt.show()


# ========================================================
# CHART 4: Instantaneous value of state S(k)
# ========================================================
plt.figure(figsize=(10, 5))
plt.fill_between(time_axis, s_k_bad, color='red', alpha=0.15, label='Accumulated fine (Bad PID)')
plt.plot(time_axis, s_k_bad, color='red', linestyle='--', linewidth=1.5)

plt.fill_between(time_axis, s_k_good, color='green', alpha=0.25, label='Accumulated Fine (Optimal PID)')
plt.plot(time_axis, s_k_good, color='green', linewidth=2)

plt.title('Distribution of the instantaneous value of state S(k) over the test interval', fontsize=14, fontweight='bold')
plt.xlabel('Time (seconds)', fontsize=12)
plt.ylabel('Instant penalty S(k) (dimensionless)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=11)
plt.savefig('reports/figures/04_instantaneous_cost.png', dpi=300)
plt.savefig('04_instantaneous_cost.png', dpi=300)
plt.show()