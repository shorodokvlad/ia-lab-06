# Teme Laborator 6 - Inteligență Artificială

Acest director conține implementările din cadrul laboratorului 6 (Comportamente reactive și vehicule Braitenberg în CoppeliaSim).

## Tema A - Evitare cu recuperare
**Fișier:** `tema/tema_a_recuperare.py`
**Nivel:** Mediu

Am implementat un comportament reactiv de bază care adaugă o stare de recuperare la cerința de oprire la obstacol. Robotul folosește o mașină de stări cu trei stări:
- `FORWARD`: merge înainte.
- `BACKWARD`: când obstacolul frontal este prea aproape (`< 0.5 m`), robotul dă înapoi pentru 1 secundă.
- `TURNING`: după mersul înapoi, robotul virează aleatoriu la stânga sau la dreapta aproximativ 90°.

Starea curentă este afișată la fiecare pas, iar scriptul continuă automat din `FORWARD` după manevra de recuperare.

## Tema B - Braitenberg cu înregistrare de date
**Fișier:** `tema/tema_b_braitenberg_logging.py`
**Nivel:** Mediu-avansat

Am extins vehiculul Braitenberg din cerința 3.5 cu înregistrarea datelor de simulare. La fiecare iterație, se salvează într-un fișier CSV (`tema/log_braitenberg.csv`) coloanele: `timestamp`, `v_left`, `v_right`, `s0`, `s1`, …, `s7`, `pos_x`, `pos_y`.

La finalul rulării (după Ctrl+C), se generează cu **Matplotlib** 3 grafice salvate ca imagini PNG:
1. Traiectoria robotului în planul XY (`pos_x` vs `pos_y`).
2. Vitezele `v_left` și `v_right` în funcție de timp.
3. Un *heatmap* al activării senzorilor în timp (`s0`–`s7` pe axa Y, timpii pe axa X).

## Tema C - Robot Explorer
**Fișier:** `tema_c_explorer.py`
**Nivel:** Avansat

Am implementat un comportament autonom de explorare bazat pe *wall-following* cu capabilități de *recuperare* în caz de blocaj frontal. 
- **Stări Implementate (RobotState):** 
  - `EXPLORING`: Robotul caută și urmărește un perete aflat în partea dreaptă utilizând un controller proporțional pe senzorii laterali.
  - `BACKWARD`: Atunci când detectează un obstacol frontal prea aproape (`< 0.4 m`), robotul oprește urmărirea și dă înapoi pentru un interval de timp fix (*1 secundă*) pentru a se debloca.
  - `TURNING`: După mersul cu spatele, robotul virează spre stânga pentru curățarea obstacolului, evitând coliziunea la următoarea încercare. Apoi revine la `EXPLORING`.
- **Salvarea Datelor:** Pe parcursul rulării, scriptul adună pozițiile `X, Y` și folosește biblioteca `matplotlib` la final pentru a genera automat harta traiectoriei globale (imagine `traiectorie_explorer.png`).

## Tema D - Braitenberg "Iubire" (Bonus)
**Fișier:** `tema_d_bonus_iubire.py`
**Vehicul:** Inspirat de vehiculul "Love" din seria Braitenberg.

- **Mecanismul Conexiunilor:** Modelează atracția magnetică și reținerea. Folosim *conexiuni ipsilaterale inhibitorii* (directe, negative):
  - Senzorii din **stânga-față** reduc viteza motorului din **stânga**. Când obstacolul se apropie pe stânga, roata stângă încetinește, în timp ce dreapta continuă cu viteza de bază. Rezultatul este un viraj clar **către** obstacolul detectat.
  - Odată ce robotul ajunge cu centrul feței la sursa stimulului (obstacolul ideal în fața sa), ambii senzori (stânga și dreapta) detectează prezența acestuia și ambele motoare sunt aduse în punctul de oprire aproape completă (`v=0`).
- **Rezultatul:** Spre deosebire de vehiculul "Frică" ce "fuge", acest vehicul "iubește" sursa, orientându-se repede înspre ea pentru ca apoi să se lipească și să contemple, oprindu-se chiar în fața ei.

Toate execuțiile trebuiesc pornite după deschiderea scenei `pioneer_lab06.ttt` în CoppeliaSim.
