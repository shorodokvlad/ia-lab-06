# Tema A - Evitare cu recuperare

Acest director conține implementarea pentru Tema A din `IA-C lab #06.md`.

## Comportament implementat

Robotul pornește înainte și monitorizează senzorii frontali. Dacă detectează un obstacol mai aproape de `0.5` m, trece prin următoarele stări:

- `FORWARD`: merge înainte.
- `BACKWARD`: revine pe o durată fixă de `1.0` s pentru a se detașa de obstacol.
- `TURNING`: virează la stânga sau dreapta aleatoriu pentru aproximativ `1.0` s.

După manevra de recuperare, robotul revine la `FORWARD` și continuă explorarea.

## Fișier

- `tema_a_recuperare.py`

## Observații

- Am folosit un `Enum` pentru `RobotState` și o funcție `next_state(current_state, dist_front)` conform cerinței.
- Duratele fixe sunt suficiente pentru o rotație aproximativă de 90° și pentru a ieși din blocaj.
- Scriptul afișează starea curentă la fiecare pas, astfel încât se poate urmări comportamentul în timp real.
