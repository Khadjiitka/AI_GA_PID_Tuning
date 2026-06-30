import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Підключення модулів проекту
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import metrics

# Налаштування папок та стилів
os.makedirs('reports/figures', exist_ok=True)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

def simulate_delta_model(Kp, Ki, Kd, steps=150, dt=0.02):
    pitch = 15.0  # Початковий нахил
    gyro_y = 0.0
    pitch_history = []
    integral_error = 0
    last_error = 0
    
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
        
    return pitch_history

def get_performance_metrics(history, dt=0.02):
    """Розраховує технічні метрики для діаграм"""
    # 1. Час стабілізації (коли помилка стає менше 0.5 градуса)
    settling_time = len(history) * dt
    for i in range(len(history)-1, 0, -1):
        if abs(history[i]) > 0.5:
            settling_time = i * dt
            break
    
    # 2. Максимальний переліт (Overshoot)
    # Шукаємо перше пересічення нуля
    overshoot = 0
    crossed_zero = False
    for val in history:
        if not crossed_zero:
            if val <= 0: crossed_zero = True
        else:
            if abs(val) > overshoot: overshoot = abs(val)
            
    return settling_time, overshoot

# --- Розрахунки ---
# Дані для "Поганого" та "Оптимального" ПІД
bad_history = simulate_delta_model(Kp=0.25, Ki=0.02, Kd=0.01)
good_history = simulate_delta_model(Kp=1.65, Ki=0.15, Kd=0.18)

bad_st, bad_os = get_performance_metrics(bad_history)
good_st, good_os = get_performance_metrics(good_history)

bad_fitness = metrics.evaluate_flight_fitness(bad_history, [0]*150)
good_fitness = metrics.evaluate_flight_fitness(good_history, [0]*150)

labels = ['Initial PID', 'Optimized AI PID']
colors = ['#ff4d4d', '#2ecc71'] # Червоний та Зелений

# ========================================================
# ДІАГРАМА 1: Порівняння Фітнес-рахунку (Penalty Score)
# ========================================================
plt.figure(figsize=(8, 6))
bars = plt.bar(labels, [bad_fitness, good_fitness], color=colors, width=0.6)
plt.title('Total System Penalty (Lower is Better)', fontsize=14, fontweight='bold', pad=20)
plt.ylabel('Fitness Score', fontsize=12)

# Додаємо цифри зверху стовпчиків
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{height:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('reports/figures/05_diagram_fitness_compare.png', dpi=300)
plt.show()

# ========================================================
# ДІАГРАМА 2: Час стабілізації та Переліт (Технічні показники)
# ========================================================
fig, ax1 = plt.subplots(figsize=(9, 6))

# Перша вісь для Часу стабілізації
x = np.arange(len(labels))
width = 0.35

rects1 = ax1.bar(x - width/2, [bad_st, good_st], width, label='Settling Time (sec)', color='#3498db')
ax1.set_ylabel('Time (seconds)', color='#3498db', fontsize=12)
ax1.tick_params(axis='y', labelcolor='#3498db')

# Друга вісь для Overshoot
ax2 = ax1.twinx()
rects2 = ax2.bar(x + width/2, [bad_os, good_os], width, label='Max Overshoot (deg)', color='#e67e22')
ax2.set_ylabel('Overshoot (degrees)', color='#e67e22', fontsize=12)
ax2.tick_params(axis='y', labelcolor='#e67e22')

plt.title('Control Quality Metrics Comparison', fontsize=14, fontweight='bold', pad=20)
ax1.set_xticks(x)
ax1.set_xticklabels(labels)

# Додаємо легенду
fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)

plt.tight_layout()
plt.savefig('reports/figures/06_diagram_metrics_compare.png', dpi=300)
plt.show()

print("\n[SUCCESS] Порівняльні діаграми згенеровано!")
print("Результати збережено в: reports/figures/05_diagram_fitness_compare.png")
print("Результати збережено в: reports/figures/06_diagram_metrics_compare.png")