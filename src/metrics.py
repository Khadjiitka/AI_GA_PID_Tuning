import numpy as np

def normalize_data(pitch, gyro_y, pitch_limit=45.0, gyro_limit=250.0):
    """
    Приведення величин до безразмерного вигляду (нормалізація) згідно з ТЗ.
    """
    pitch_norm = pitch / pitch_limit
    gyro_norm = gyro_y / gyro_limit
    return pitch_norm, gyro_norm

def calculate_instantaneous_cost(pitch_norm, gyro_norm, w_theta=0.7, w_omega=0.3):
    """
    Формула з ТЗ: S(k) = w_theta * |\Delta theta(k)| + w_omega * |\Delta omega(k)|
    Оцінює якість стану системи на конкретному кроці k.
    """
    return w_theta * abs(pitch_norm) + w_omega * abs(gyro_norm)

def evaluate_flight_fitness(pitch_history, gyro_history, dt=0.02, w_os=15.0, w_settle=10.0):
    """
    Підсумкова функція Fitness за весь інтервал часу (мінімізується в ГА).
    Включает інтеграл вартості S(k)*dt + штрафи за Overshoot і Settling Time.
    """
    pitch_history = np.array(pitch_history)
    gyro_history = np.array(gyro_history)
    
    # 1. Перевірка аварійного бар'єра (Safety Layer)
    if np.any(abs(pitch_history) > 45.0):
        return 9999.0  # Максимальний штраф (Emergency Trigger)

    # 2. Інтеграл миттєвої вартості
    total_integral = 0
    for p, g in zip(pitch_history, gyro_history):
        p_norm, g_norm = normalize_data(p, g)
        total_integral += calculate_instantaneous_cost(p_norm, g_norm) * dt
        
    # 3. Розрахунок Перерегулювання (Overshoot)
    overshoot = max(abs(pitch_history)) if len(pitch_history) > 0 else 0
    
    # 4. Розрахунок Часу заспокоєння (Settling Time)
    settling_time = 0
    for i in range(len(pitch_history) - 1, -1, -1):
        if abs(pitch_history[i]) > 1.0:
            settling_time = i * dt
            break

    # Підсумкова формула мінімізації
    total_fitness = total_integral + (w_os * overshoot) + (w_settle * settling_time)
    return float(total_fitness)