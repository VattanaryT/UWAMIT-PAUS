# UWAMIT-PAUS

This project contains scripts and configurations for controlling stepper motors and automating fiber positioning using Automation1 and Python.

---

## Folder Structure

### `config/`
Motor configuration files:
- `VirtualStepperMotor.mcd` – Use this for **testing without hardware** (motor not physically connected).
- `StepperMotor.mcd` – Default configuration for the **BMS60 controller** used in PAUS. Ensure you're connected via USB before use.

---

### `notes/`
- `Notes.txt` – A record of saved fiber positions.

---

### `main/`
Commonly used automation scripts:
- `1_test_position.ascript` – Rotates the motor through each fiber position for **testing**.
- `2_psoscript.ascript` – Generates signals based on **20 fiber positions** using a **single controller**.
- `3_integrated_controllers.ascript` – Generates signals for all 20 positions **plus** a single signal for the transition from the 20th back to the 1st position. Requires **both controllers**.

---

### `userinterface_python_exec/`
Python-based interface for automation:
- Contains executable scripts designed to run without Automation1 Studio.
- *Currently under development.*

---

## Additional Support

Go to Aerotech's Automation1 document page: https://help.aerotech.com/automation1/Content/MainPage.htm 
or contact Aerotech's technical support.