import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

# 1. Typed Models for Actions
class Action(BaseModel):
    fan_change_rack1: int # -1 (decrease), 0 (keep), 1 (increase)
    fan_change_rack2: int
    fan_change_rack3: int

# 2. State Management
class State:
    def __init__(self):
        self.rack_temps = [30.0, 32.0, 28.0]
        self.fan_speeds = [2, 2, 2] # Scale 1-5
        self.power_usage = 300
        self.step_count = 0

    def reset(self):
        # Start with random high temperatures
        self.rack_temps = [random.uniform(28.0, 35.0) for _ in range(3)]
        self.fan_speeds = [2, 2, 2]
        self.power_usage = sum(self.fan_speeds) * 50
        self.step_count = 0

current_state = State()

# 3. Required Endpoints
@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/reset")
def reset():
    current_state.reset()
    return get_state()

@app.get("/state")
def get_state():
    return {
        "rack_temps": [round(t, 2) for t in current_state.rack_temps],
        "fan_speeds": current_state.fan_speeds,
        "power_usage": current_state.power_usage,
        "step_count": current_state.step_count
    }

# 4. Step Logic and Graders
def calculate_score(temp):
    """Partial progress signal: 1.0 if perfect (<25C), drops to 0.0 if too hot."""
    if temp <= 25.0: return 1.0
    if temp >= 35.0: return 0.0
    return round(1.0 - ((temp - 25.0) / 10.0), 2)

@app.post("/step")
def step(action: Action):
    current_state.step_count += 1
    
    # Apply Actions: Update fan speeds (clamp between 1 and 5)
    current_state.fan_speeds[0] = max(1, min(5, current_state.fan_speeds[0] + action.fan_change_rack1))
    current_state.fan_speeds[1] = max(1, min(5, current_state.fan_speeds[1] + action.fan_change_rack2))
    current_state.fan_speeds[2] = max(1, min(5, current_state.fan_speeds[2] + action.fan_change_rack3))
    
    # Simple Physics: Heat naturally increases, fans decrease it
    for i in range(3):
        base_heat = 1.5
        cooling_power = current_state.fan_speeds[i] * 0.8
        current_state.rack_temps[i] += (base_heat - cooling_power)
        
    # Calculate total power
    current_state.power_usage = sum(current_state.fan_speeds) * 50
    
    # GRADERS (0.0 to 1.0)
    # Task 1 (Easy): Cool down Rack 1
    score_easy = calculate_score(current_state.rack_temps[0])
    
    # Task 2 (Medium): Cool down all racks
    score_medium = sum([calculate_score(t) for t in current_state.rack_temps]) / 3.0
    
    # Task 3 (Hard): Cool all racks AND keep power under 500W
    power_penalty = 1.0 if current_state.power_usage <= 500 else 0.5
    score_hard = round(score_medium * power_penalty, 2)
    
    return {
        "state": get_state(),
        "scores": {
            "easy": score_easy,
            "medium": score_medium,
            "hard": score_hard
        },
        "done": current_state.step_count >= 15 # End episode after 15 steps
    }

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()