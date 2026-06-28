# Automatic PID Controller Tuning Subsystem

> **Data-driven Genetic Algorithm optimization of PID controllers for robotic balancing platforms.**

---

# 📌 Overview

This project implements an **intelligent software subsystem** for the **automatic tuning of PID controllers** using a **Genetic Algorithm (GA)**.

Unlike classical tuning approaches based solely on mathematical models, this project follows a **data-driven methodology**, where optimization is performed using telemetry collected from a real balancing platform based on an **ESP32 microcontroller**.

The developed framework automatically searches for optimal **Kp**, **Ki**, and **Kd** coefficients while respecting physical safety constraints of the robotic system.

---

# Project Objectives

The project consists of five major engineering stages:

- **Telemetry Collection** <br> Collect IMU data from the balancing platform.<br> Build a real-time telemetry pipeline.
- **Data Processing** <br> Clean and normalize experimental signals. <br> Prepare datasets for optimization.
- **Fitness Function Development** <br> Convert physical stability characteristics into a mathematical optimization criterion.
- **Genetic Algorithm Optimization** <br> Search for optimal PID parameters.<br> Prevent dangerous controller configurations.
- **Experimental Evaluation** <br> Compare optimized and baseline controllers.<br> Generate analytical visualizations.

---

# Workflow

The optimization pipeline consists of seven sequential stages.

## 1️⃣ Experimental Platform Identification

Collect raw IMU telemetry from previous or live experiments.

## 2️⃣ Motor Balance Estimation

Estimate actuator imbalance and compensate for mechanical offsets.

## 3️⃣ Working Thrust Detection

Determine safe PWM operating limits.

| Parameter   | Value |
| ----------- | ----: |
| Minimum PWM |   600 |
| Maximum PWM |  1800 |

These limits prevent:

- motor stall
- overheating
- unsafe operation

## 4️⃣ Fitness Function Development

Safety constraints:

| Condition     | Angle |
| ------------- | ----: |
| Stable Zone   |   ±7° |
| Critical Zone |  ±10° |

The fitness function penalizes:

- overshoot
- oscillation
- vibration
- long settling time

## 5️⃣ Genetic Algorithm Optimization

The optimizer searches for the best PID parameters inside a virtual simulation before applying them to real hardware.

## 6️⃣ Experimental Validation

Optimized parameters are transmitted to the ESP32 controller and evaluated on the real balancing platform.

## 7️⃣ Fitness Refinement

Simulation results are compared with physical experiments to improve future optimization accuracy.

---

# 📄 File Description

| File                                | Description                                                                                                                                                                   |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **config.py**                       | Global configuration, safety limits, optimizer parameters                                                                                                                     |
| **data_loader.py**                  | CSV telemetry parser                                                                                                                                                          |
| **database.py**                     | SQLite data access layer                                                                                                                                                      |
| **metrics.py**                      | Fitness function implementation                                                                                                                                               |
| **ga_optimizer.py**                 | Genetic Algorithm implementation                                                                                                                                              |
| **main.py**                         | Main execution pipeline                                                                                                                                                       |
| **generate_presentation_charts.py** | Performance visualization                                                                                                                                                     |
| **generate_remaining_charts.py**    | Additional analytical plots                                                                                                                                                   |
| **01_data_identification.ipynb**    | A research notebook focused on secondary data parsing, signal cleaning, noise filtering from the raw IMU logs, and validating the telemetry import pipeline                   |
| **02_fitness_development.ipynb**    | An algorithmic laboratory used to model and simulate the fitness equations, tune the balance coefficients, and experiment with the severity of mathematical penalty functions |
| **03_genetic_algorithm.ipynb**      | The sandbox where individual genetic operators (tournament selection, arithmetic blending, and chromosomal mutations) were prototyped and validated before deployment         |

---

# 🧬 Genetic Algorithm Methodology

Each chromosome represents:

```
[Kp, Ki, Kd]
```

### Initialization

- Population size: **20**

---

### Simulation

Each candidate controller is evaluated on a virtual balancing model.

- Initial angle: **7°**
- Simulation length: **150 iterations**

---

### Fitness Evaluation

The optimization objective is **minimize(Fitness)**
<br><br>
Controllers exceeding **±10°**
<br><br>
receive an emergency penalty:
<br> <br>
**Fitness = 99999**

---

### Selection

Tournament Selection

---

### Elitism

The two best individuals are copied unchanged into the next generation.

---

### Crossover

Arithmetic Blending

---

### Mutation

Mutation probability:

```
15%
```

Gaussian perturbation is applied to individual PID coefficients.

---

### Evolution

```
15 Generations
```

---

# 📈 Experimental Results

## Chart 1. System Recovery Profile

<p align="center">
  <img src="PASTE_YOUR_PERMALINK_HERE" width="800">
</p>

<p align="center">
<i><b>Figure 1.</b> Platform pitch angle during stabilization before and after PID optimization.</i>
</p>

This chart illustrates the evolution of the platform's pitch angle over time. The baseline controller (red dashed curve) exhibits large oscillations reaching approximately **±13°**, indicating an unstable control system that could potentially damage the hardware. In contrast, the PID parameters optimized by the **Genetic Algorithm** (green solid curve) provide a well-damped response, returning the platform from an initial **15°** disturbance to the equilibrium position in approximately **1.5 seconds** while limiting overshoot to less than **10%** of the initial error.

---

## Chart 2. Genetic Algorithm Convergence

<p align="center">
  <img src="PASTE_YOUR_PERMALINK_HERE" width="800">
</p>

<p align="center">
<i><b>Figure 2.</b> Evolution of the minimum fitness score during Genetic Algorithm optimization.</i>
</p>

The convergence curve presents the best fitness value obtained in each generation. The staircase-shaped profile demonstrates the effectiveness of the **Elitism** strategy: horizontal sections correspond to preserving the best solution across generations, whereas sharp decreases indicate successful crossover or mutation events that produced a superior PID configuration. The overall downward trend confirms stable convergence toward an improved controller.

---

## Chart 3. Angular Velocity Profile

<p align="center">
  <img src="PASTE_YOUR_PERMALINK_HERE" width="800">
</p>

<p align="center">
<i><b>Figure 3.</b> Comparison of angular velocity before and after PID optimization.</i>
</p>

This figure compares the platform's angular velocity during stabilization. The initial controller produces rapid, high-frequency velocity fluctuations caused by aggressive motor commands, increasing electrical load and mechanical wear. After optimization, the controller generates a significantly smoother velocity profile that gradually approaches zero, demonstrating improved damping characteristics and more efficient actuator behavior.

---

## Chart 4. Instantaneous State Cost Distribution

<p align="center">
  <img src="PASTE_YOUR_PERMALINK_HERE" width="800">
</p>

<p align="center">
<i><b>Figure 4.</b> Distribution of the instantaneous penalty function throughout stabilization.</i>
</p>

The graph visualizes the instantaneous penalty function **S(k)** accumulated during the stabilization process. The area under the curve represents the overall operational cost experienced by the balancing platform. The baseline controller accumulates a large and continuously increasing penalty due to persistent instability, whereas the optimized controller concentrates most of its cost within the initial stabilization period before rapidly converging toward zero. This behavior confirms that the proposed fitness function effectively guides the Genetic Algorithm toward highly stable PID parameters.

---

# 💻 Technologies

<a href="https://www.python.org"><img src="https://skillicons.dev/icons?i=python" height="55"/></a>
<a href="https://numpy.org"><img src="https://go-skill-icons.vercel.app/api/icons?i=numpy" height="55"/></a>
<a href="https://pandas.pydata.org"><img src="https://go-skill-icons.vercel.app/api/icons?i=pandas" height="55"/></a>
<a href="https://scipy.org"><img src="https://go-skill-icons.vercel.app/api/icons?i=scipy" height="55"/></a>
<a href="https://matplotlib.org"><img src="https://go-skill-icons.vercel.app/api/icons?i=matplotlib" height="55"/></a>
<a href="https://sqlite.org"><img src="https://skillicons.dev/icons?i=sqlite" height="55"/></a>
<a href="https://jupyter.org"><img src="https://go-skill-icons.vercel.app/api/icons?i=jupyter" height="55"/></a>

---

# 🚀 Future Improvements

- Bayesian Optimization
- Particle Swarm Optimization (PSO)
- Differential Evolution
- Real-time telemetry dashboard
- Reinforcement Learning integration
- Multi-axis stabilization
- Hardware-in-the-loop optimization

---

# 📜 License

This project was developed for research and educational purposes.
