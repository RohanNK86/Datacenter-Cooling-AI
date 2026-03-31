# Data Center Cooling Optimizer OpenEnv

## Description
A real-world simulation of a data center where an agent must manage the cooling systems (fan speeds) of 3 server racks.

## Action Space
Agent provides a JSON object altering fan speeds (-1, 0, or 1) for each of the 3 racks.

## Observation Space
- `rack_temps`: Float array of current temperatures.
- `fan_speeds`: Integer array of current fan speeds (1-5).
- `power_usage`: Total power consumption in Watts.

## Setup Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Run environment: `uvicorn env:app --port 7860`
3. Run inference: `python inference.py`