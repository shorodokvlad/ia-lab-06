"""
Tema C - Robot Explorer
IA Lab #06 - Inteligență Artificială 2025-2026
"""
import time
import enum
import matplotlib.pyplot as plt
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

V_BASE       = 3.0    # rad/s - viteza de baza
TARGET_DIST  = 0.4    # metri
K_P          = 3.0    # coeficient proportional
FRONT_STOP   = 0.4    # metri
SENSOR_MAX   = 1.0    # metri
BACKWARD_TIME = 1.0
TURN_TIME = 1.0

RIGHT_SENSORS = [8, 9]
FRONT_SENSORS = [3, 4]

class RobotState(enum.Enum):
    EXPLORING = 1
    BACKWARD = 2
    TURNING = 3

def read_min_dist(sim, sensors, indices):
    min_dist = SENSOR_MAX
    for idx in indices:
        result, dist, *_ = sim.readProximitySensor(sensors[idx])
        if result and dist < min_dist:
            min_dist = dist
    return min_dist

def main():
    client = RemoteAPIClient()
    sim = client.require('sim')

    robot       = sim.getObject('/PioneerP3DX')
    left_motor  = sim.getObject('/PioneerP3DX/leftMotor')
    right_motor = sim.getObject('/PioneerP3DX/rightMotor')
    sensors     = [sim.getObject(f'/PioneerP3DX/ultrasonicSensor[{i}]') for i in range(16)]

    sim.startSimulation()
    print("Tema C - Robot Explorer pornit. (Ctrl+C pentru oprire)")

    state = RobotState.EXPLORING
    state_start_time = time.time()
    
    xs, ys = [], []

    try:
        while True:
            current_time = time.time()
            dist_right = read_min_dist(sim, sensors, RIGHT_SENSORS)
            dist_front = read_min_dist(sim, sensors, FRONT_SENSORS)
            
            pos = sim.getObjectPosition(robot, sim.handle_world)
            xs.append(pos[0])
            ys.append(pos[1])

            if state == RobotState.EXPLORING:
                if dist_front < FRONT_STOP:
                    state = RobotState.BACKWARD
                    state_start_time = current_time
                    v_left, v_right = -V_BASE, -V_BASE
                    state_str = f"BLOCAJ: DA INAPOI (frontal={dist_front:.3f} m)"
                else:
                    if dist_right >= SENSOR_MAX * 0.95:
                        v_left, v_right = V_BASE, V_BASE * 0.5
                        state_str = "CAUTA PERETE"
                    else:
                        error   = dist_right - TARGET_DIST
                        v_left  = V_BASE + K_P * error
                        v_right = V_BASE - K_P * error
                        cap = V_BASE * 1.5
                        v_left  = max(-cap, min(cap, v_left))
                        v_right = max(-cap, min(cap, v_right))
                        state_str = f"URMARIRE dr={dist_right:.3f} m err={error:+.3f} m"
                        
            elif state == RobotState.BACKWARD:
                v_left, v_right = -V_BASE, -V_BASE
                state_str = "RECUPERARE: MERS INAPOI"
                if current_time - state_start_time > BACKWARD_TIME:
                    state = RobotState.TURNING
                    state_start_time = current_time
                    
            elif state == RobotState.TURNING:
                v_left, v_right = -V_BASE, V_BASE
                state_str = "RECUPERARE: VIRAJ STANGA"
                if current_time - state_start_time > TURN_TIME:
                    state = RobotState.EXPLORING
                    state_start_time = current_time

            sim.setJointTargetVelocity(left_motor,  v_left)
            sim.setJointTargetVelocity(right_motor, v_right)
            print(f"{state_str:<45} vS={v_left:+.2f} vD={v_right:+.2f}")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nOprire explorer.")
    finally:
        sim.setJointTargetVelocity(left_motor,  0.0)
        sim.setJointTargetVelocity(right_motor, 0.0)
        sim.stopSimulation()
        
        # Generare grafic
        if xs and ys:
            print("Generare grafic traiectorie...")
            try:
                plt.figure(figsize=(8, 8))
                plt.plot(xs, ys, label="Traiectorie")
                plt.scatter(xs[0], ys[0], color='green', marker='o', label="Start")
                plt.scatter(xs[-1], ys[-1], color='red', marker='x', label="Stop")
                plt.title('Traiectorie Robot Explorer (Tema C)')
                plt.xlabel('X [m]')
                plt.ylabel('Y [m]')
                plt.legend()
                plt.grid(True)
                plt.savefig('tema/traiectorie_explorer.png')
                print("Grafic salvat ca 'tema/traiectorie_explorer.png'.")
            except Exception as e:
                print(f"Eroare la generarea graficului: {e}")

if __name__ == '__main__':
    main()
