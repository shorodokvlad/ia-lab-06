# Teme Laborator 6 - Inteligență Artificială

Acest director conține implementările pentru temele opționale C și D din cadrul laboratorului 6 (Comportamente reactive și vehicule Braitenberg în CoppeliaSim).

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
