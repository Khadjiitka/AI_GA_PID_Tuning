import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Подключаем модули проекта
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import metrics

os.makedirs('reports/figures', exist_ok=True)
plt.rcParams['font.family'] = 'DejaVu Sans'

# Воспроизводим ту же симуляцию дельта-модели
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

# Получаем данные для плохого и хорошего регуляторов
pitch_bad, gyro_bad = simulate_delta_model(Kp=0.25, Ki=0.02, Kd=0.01)
pitch_good, gyro_good = simulate_delta_model(Kp=1.65, Ki=0.15, Kd=0.18)

time_axis = np.arange(150) * 0.02

# Рассчитываем динамику изменения мгновенной стоимости S(k) для обоих случаев
s_k_bad = [metrics.calculate_instantaneous_cost(*metrics.normalize_data(p, g)) for p, g in zip(pitch_bad, gyro_bad)]
s_k_good = [metrics.calculate_instantaneous_cost(*metrics.normalize_data(p, g)) for p, g in zip(pitch_good, gyro_good)]


# ========================================================
# ГРАФИК 3: Переходный процесс угловой скорости (Gyro Y)
# ========================================================
plt.figure(figsize=(10, 5))
plt.plot(time_axis, gyro_bad, color='orange', linestyle='--', label='Начальный ПИД (Высокая угловая скорость)', linewidth=2)
plt.plot(time_axis, gyro_good, color='blue', label='Оптимизированный ШІ ПИД (Стабильное затухание)', linewidth=2.5)
plt.axhline(0, color='black', linestyle=':', alpha=0.5)
plt.title('📊 Динамика изменения угловой скорости (Gyro Y) во времени', fontsize=14, fontweight='bold')
plt.xlabel('Час (секунди)', fontsize=12)
plt.ylabel('Угловая скорость Pitch Rate (град/сек)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=11)
plt.savefig('reports/figures/03_gyro_response.png', dpi=300)
plt.savefig('03_gyro_response.png', dpi=300)
plt.show()


# ========================================================
# ГРАФИК 4: Мгновенная стоимость состояния S(k)
# ========================================================
plt.figure(figsize=(10, 5))
plt.fill_between(time_axis, s_k_bad, color='red', alpha=0.15, label='Накопленный штраф (Плохой ПИД)')
plt.plot(time_axis, s_k_bad, color='red', linestyle='--', linewidth=1.5)

plt.fill_between(time_axis, s_k_good, color='green', alpha=0.25, label='Накопленный штраф (Оптимальный ПИД)')
plt.plot(time_axis, s_k_good, color='green', linewidth=2)

plt.title('📉 Распределение мгновенной стоимости состояния S(k) на интервале теста', fontsize=14, fontweight='bold')
plt.xlabel('Час (секунди)', fontsize=12)
plt.ylabel('Мгновенный штраф S(k) (безразмерный)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=11)
plt.savefig('reports/figures/04_instantaneous_cost.png', dpi=300)
plt.savefig('04_instantaneous_cost.png', dpi=300)
plt.show()

print("🏁 Дополнительные графики (03_gyro_response и 04_instantaneous_cost) успешно созданы!")