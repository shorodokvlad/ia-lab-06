"""
Tema B - Braitenberg cu înregistrare de date (nivel: mediu-avansat)
IA Lab #06 - Inteligență Artificială 2025-2026

Extinde cerința 3.5 cu înregistrarea datelor de simulare.
La fiecare iterație, salvează într-un fișier CSV (`tema/log_braitenberg.csv`)
coloanele: `timestamp`, `v_left`, `v_right`, `s0`, `s1`, …, `s7`, `pos_x`, `pos_y`.

La finalul rulării (după Ctrl+C), generează cu Matplotlib 3 grafice salvate ca imagini PNG:
1. Traiectoria robotului în planul XY (`pos_x` vs `pos_y`).
2. Vitezele `v_left` și `v_right` în funcție de timp.
3. Un heatmap al activării senzorilor în timp (`s0`–`s7` pe axa Y, timpii pe axa X).
"""
import time
import csv
import matplotlib.pyplot as plt
import numpy as np
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

V_BASE   = 3.0   # rad/s - viteza de baza (robot fara obstacole in fata)
V_MAX    = 6.0   # rad/s - viteza maxima permisa
K_SENSOR = 6.0   # factor de amplificare a influentei senzorilor
SENSOR_MAX = 1.0 # metri - raza maxima senzor

# Ponderile senzorilor: (w_motor_stang, w_motor_drept)
# Indecsi 0..7 = jumatatea frontala a robotului
# Conexiuni ipsilaterale (directe) => tip "Frica" (evitare):
#   senzor stanga excita motorul stang → roata stanga mai rapida → vireaza DREAPTA (departe)
#   senzor dreapta excita motorul drept → roata dreapta mai rapida → vireaza STANGA (departe)
WEIGHTS = [
    (+0.5, -0.5),   # S0  fata-stanga-ext   → excita stanga, inhiba dreapta → vireaza dreapta
    (+1.0, -1.0),   # S1  fata-stanga
    (+1.5, -1.5),   # S2  fata-centru-st
    (+2.0, -2.0),   # S3  fata-centru-st
    (-2.0, +2.0),   # S4  fata-centru-dr    → excita dreapta, inhiba stanga → vireaza stanga
    (-1.5, +1.5),   # S5  fata-centru-dr
    (-1.0, +1.0),   # S6  fata-dreapta
    (-0.5, +0.5),   # S7  fata-dreapta-ext
]


def braitenberg_velocities(sim, sensors):
    """
    Calculeaza vitezele Braitenberg pentru evitarea obstacolelor.

    Fiecare senzor activat contribuie proportional cu apropierea
    de obstacol, prin ponderile definite in WEIGHTS.

    Args:
        sim: obiectul API CoppeliaSim.
        sensors: lista handle-urilor tuturor senzorilor.

    Returns:
        tuple (v_stang, v_drept) in rad/s.
    """
    v_left  = V_BASE
    v_right = V_BASE

    for i, (w_l, w_r) in enumerate(WEIGHTS):
        result, distance, *_ = sim.readProximitySensor(sensors[i])
        if result:
            # Normalizare: obstacol aproape => proximity=1, departe => proximity=0
             proximity = 1.0 - (distance / SENSOR_MAX)
             proximity = max(0.0, min(1.0, proximity))

             v_left  += K_SENSOR * w_l * proximity
             v_right += K_SENSOR * w_r * proximity

    # Limitare la intervalul [-V_MAX, +V_MAX]
    v_left  = max(-V_MAX, min(V_MAX, v_left))
    v_right = max(-V_MAX, min(V_MAX, v_right))

    return v_left, v_right


def main():
    client = RemoteAPIClient()
    sim = client.require('sim')

    left_motor  = sim.getObject('/PioneerP3DX/leftMotor')
    right_motor = sim.getObject('/PioneerP3DX/rightMotor')
    robot       = sim.getObject('/PioneerP3DX')
    sensors     = [
        sim.getObject(f'/PioneerP3DX/ultrasonicSensor[{i}]')
        for i in range(16)
    ]

    # Initializare liste pentru date
    timestamps = []
    v_lefts = []
    v_rights = []
    sensor_proximities = [[] for _ in range(8)]  # s0 to s7
    positions_x = []
    positions_y = []

    sim.startSimulation()
    print("Vehicul Braitenberg cu înregistrare date pornit. Ctrl+C pentru oprire.\n")

    try:
        iteration = 0
        while True:
            timestamp = time.time()
            v_left, v_right = braitenberg_velocities(sim, sensors)

            # Citire proximitati pentru senzorii frontali 0-7
            proximities = []
            for i in range(8):
                result, distance, *_ = sim.readProximitySensor(sensors[i])
                if result:
                    proximity = 1.0 - (distance / SENSOR_MAX)
                    proximity = max(0.0, min(1.0, proximity))
                else:
                    proximity = 0.0
                proximities.append(proximity)

            # Pozitia robotului
            position = sim.getObjectPosition(robot)
            pos_x, pos_y = position[0], position[1]

            # Adaugare la liste
            timestamps.append(timestamp)
            v_lefts.append(v_left)
            v_rights.append(v_right)
            for i in range(8):
                sensor_proximities[i].append(proximities[i])
            positions_x.append(pos_x)
            positions_y.append(pos_y)

            sim.setJointTargetVelocity(left_motor,  v_left)
            sim.setJointTargetVelocity(right_motor, v_right)

            # Afisare la fiecare ~1 secunda (20 iteratii x 0.05s)
            if iteration % 20 == 0:
                print(f"v_stang={v_left:+.2f} rad/s  |  v_drept={v_right:+.2f} rad/s")

            iteration += 1
            time.sleep(0.05)   # 20 Hz

    except KeyboardInterrupt:
        print("\nOprire vehicul Braitenberg. Salvarea datelor...")

        # Scriere CSV
        with open('tema/log_braitenberg.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp', 'v_left', 'v_right'] + [f's{i}' for i in range(8)] + ['pos_x', 'pos_y'])
            for i in range(len(timestamps)):
                row = [timestamps[i], v_lefts[i], v_rights[i]]
                for j in range(8):
                    row.append(sensor_proximities[j][i])
                row.extend([positions_x[i], positions_y[i]])
                writer.writerow(row)

        print("Date salvate în tema/log_braitenberg.csv")

        # Generare grafice
        # 1. Traiectoria
        plt.figure(figsize=(8, 6))
        plt.plot(positions_x, positions_y, 'b-', linewidth=2)
        plt.title('Traiectoria robotului în planul XY')
        plt.xlabel('Poziție X (m)')
        plt.ylabel('Poziție Y (m)')
        plt.grid(True)
        plt.axis('equal')
        plt.savefig('tema/trajectory_braitenberg.png')
        plt.close()

        # 2. Vitezele în timp
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, v_lefts, 'r-', label='Viteză stânga', linewidth=1.5)
        plt.plot(timestamps, v_rights, 'b-', label='Viteză dreapta', linewidth=1.5)
        plt.title('Vitezele motoarelor în funcție de timp')
        plt.xlabel('Timp (s)')
        plt.ylabel('Viteză (rad/s)')
        plt.legend()
        plt.grid(True)
        plt.savefig('tema/velocities_braitenberg.png')
        plt.close()

        # 3. Heatmap senzorilor
        sensor_matrix = np.array(sensor_proximities)  # (8, len(timestamps))
        plt.figure(figsize=(12, 6))
        plt.imshow(sensor_matrix, aspect='auto', cmap='hot', origin='lower')
        plt.title('Heatmap activare senzori frontali (s0-s7)')
        plt.xlabel('Timp (iterații)')
        plt.ylabel('Senzor')
        plt.yticks(range(8), [f's{i}' for i in range(8)])
        plt.colorbar(label='Proximitate (0-1)')
        plt.savefig('tema/sensors_heatmap_braitenberg.png')
        plt.close()

        print("Grafice salvate: trajectory_braitenberg.png, velocities_braitenberg.png, sensors_heatmap_braitenberg.png")

    finally:
        sim.setJointTargetVelocity(left_motor,  0.0)
        sim.setJointTargetVelocity(right_motor, 0.0)
        sim.stopSimulation()


if __name__ == '__main__':
    main()