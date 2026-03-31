# 🥶 Data Center Cooling Optimizer - OpenEnv

![OpenEnv Hackathon](https://img.shields.io/badge/OpenEnv-Hackathon_Round_1-blue)
![Python](https://img.shields.io/badge/Python-3.9+-yellow)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green)

## 📖 Project Overview
This project is an interactive, real-world Reinforcement Learning (RL) environment built for the **OpenEnv Hackathon**. 

It simulates a data center where an AI agent must manage the cooling systems (fan speeds) of 3 server racks. The agent's goal is to learn the physics of the room to keep the servers from overheating while simultaneously minimizing the electricity used by the cooling fans.

## ⚙️ The Environment API

### 👁️ Observation Space (The State)
At each step, the AI receives a JSON object representing the current physical state of the server room:
* `rack_temps` (Float Array): The current temperatures of the 3 server racks (Target: ≤ 25.0°C).
* `fan_speeds` (Integer Array): The current speed level of the 3 fans, ranging from 1 (minimum) to 5 (maximum).
* `power_usage` (Integer): Total power consumption in Watts based on active fan speeds (Target: ≤ 500W).

### 🎮 Action Space
The agent responds with a JSON object containing three integers (`-1`, `0`, or `1`), dictating how to adjust the fans:
* `-1`: Decrease fan speed
* `0`: Maintain current fan speed
* `1`: Increase fan speed

## 🏆 Tasks & Grading Logic
The environment automatically grades the AI's performance from `0.0` to `1.0` across three difficulty tiers:

1. **Easy:** Cool down Rack 1 below 25.0°C.
2. **Medium:** Cool down all 3 racks below 25.0°C.
3. **Hard:** Cool down all 3 racks below 25.0°C **AND** maintain total power consumption strictly under 500 Watts. Exceeding 500W results in a severe 50% score penalty.

## 📂 Repository Structure
* `env.py`: The core FastAPI server containing the environment physics, state management, and grading logic.
* `inference.py`: The baseline LLM agent script using the OpenAI client format to solve the environment.
* `openenv.yaml`: The strict environment specification required by the hackathon.
* `Dockerfile`: Containerization instructions for cloud deployment.
* `requirements.txt`: Python dependencies.

## 🚀 How to Run Locally

**1. Install Dependencies**
```bash
pip install -r requirements.txt
