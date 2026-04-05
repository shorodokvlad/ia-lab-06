"""
Tema A - Evitare cu recuperare
IA Lab #06 - Inteligență Artificială 2025-2026

Comportament reactiv cu recuperare la blocaj frontal.
"""
import random
import time
from enum import Enum
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

V_FORWARD     = 2.0    # rad/s - viteza de deplasare inainte
V_BACKWARD    = -1.5   # rad/s - viteza de mers inapoi
V_TURN        = 1.8    # rad/s - viteza motoare la rotatie
STOP_DISTANCE = 0.5    # metri - distanta la care robotul activeaza recuperarea
BACK_DURATION = 1.0    # secunde - durata mersului inapoi
TURN_DURATION = 1.0    # secunde - durata rotirii la 90° aproximativ
FRONT_SENSORS = [2, 3, 4, 5]  # indicii senzorilor frontali
SENSOR_MAX    = 1.0    # metri - valoare cand senzorul nu detecteaza nimic


class RobotState(Enum):
    FORWARD = 'FORWARD'
    BACKWARD = 'BACKWARD'
    TURNING = 'TURNING'


def next_state(current_state, dist_front):
    """Returneaza urmatoarea stare pe baza starii curente si a distantei frontale."""
    if current_state == RobotState.FORWARD:
        return RobotState.BACKWARD if dist_front < STOP_DISTANCE else RobotState.FORWARD
    if current_state == RobotState.BACKWARD:
        return RobotState.TURNING
    if current_state == RobotState.TURNING:
        return RobotState.FORWARD
    return RobotState.FORWARD


def get_min_front_distance(sim, sensors, front_indices):
    """Returneaza distanta minima detectata de senzorii frontali."""
    min_dist = SENSOR_MAX
    for idx in front_indices:
        result, distance, *_ = sim.readProximitySensor(sensors[idx])
        if result and distance < min_dist:
            min_dist = distance
    return min_dist


def main():
    client = RemoteAPIClient()
    sim = client.require('sim')

    left_motor = sim.getObject('/PioneerP3DX/leftMotor')
    right_motor = sim.getObject('/PioneerP3DX/rightMotor')
    sensors = [
        sim.getObject(f'/PioneerP3DX/ultrasonicSensor[{i}]')
        for i in range(16)
    ]

    sim.startSimulation()
    print('Tema A - Evitare cu recuperare')
    print(f'Stop la obstacol < {STOP_DISTANCE} m. (Ctrl+C pentru oprire)')

    state = RobotState.FORWARD
    turn_direction = None
    state_start_time = time.time()

    try:
        while True:
            dist_front = get_min_front_distance(sim, sensors, FRONT_SENSORS)
            new_state = next_state(state, dist_front)

            if state != new_state:
                state = new_state
                state_start_time = time.time()
                if state == RobotState.TURNING:
                    turn_direction = random.choice(['LEFT', 'RIGHT'])

            elapsed = time.time() - state_start_time

            if state == RobotState.FORWARD:
                v_left = V_FORWARD
                v_right = V_FORWARD
                action = f'FORWARD - dist_front={dist_front:.3f} m'

            elif state == RobotState.BACKWARD:
                v_left = V_BACKWARD
                v_right = V_BACKWARD
                action = f'BACKWARD ({elapsed:.2f}/{BACK_DURATION:.2f} s)'
                if elapsed >= BACK_DURATION:
                    state = next_state(state, dist_front)
                    state_start_time = time.time()
                    turn_direction = random.choice(['LEFT', 'RIGHT'])
                    continue

            elif state == RobotState.TURNING:
                if turn_direction == 'LEFT':
                    v_left, v_right = -V_TURN, V_TURN
                else:
                    v_left, v_right = V_TURN, -V_TURN
                action = f'TURNING {turn_direction} ({elapsed:.2f}/{TURN_DURATION:.2f} s)'
                if elapsed >= TURN_DURATION:
                    state = next_state(state, dist_front)
                    state_start_time = time.time()
                    continue

            sim.setJointTargetVelocity(left_motor,  v_left)
            sim.setJointTargetVelocity(right_motor, v_right)
            print(f'[{state.value:<8}] {action:<40}  vL={v_left:+.2f} vR={v_right:+.2f}')

            time.sleep(0.05)

    except KeyboardInterrupt:
        print('\nOprire manuala.')
    finally:
        sim.setJointTargetVelocity(left_motor,  0.0)
        sim.setJointTargetVelocity(right_motor, 0.0)
        sim.stopSimulation()


if __name__ == '__main__':
    main()
