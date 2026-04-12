import os
import requests
import json
import time
from openai import OpenAI

# Load variables from .env file if it exists
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

# 1. Point the OpenAI client to Google's Gemini servers!
API_BASE_URL = os.getenv("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")

# We'll hook this up to the powerful Pro model for the best logic
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash") 

# 2. Put your REAL Gemini key right here (starts with AIza...)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "GEMINI_API_KEY") 

# 3. Your live Hugging Face Space URL
ENV_URL = os.getenv("ENV_URL", "https://rohannk-datacenter-openenv.hf.space")

# We are strictly using the OpenAI client to satisfy the hackathon rules
client = OpenAI(
    base_url=API_BASE_URL, 
    api_key=GEMINI_API_KEY
)

def run_inference():
    import argparse
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default=os.environ.get("TASK", "task_1_easy"))
    parser.add_argument("--task-id", type=str, dest="task_id", default=None)
    args, _ = parser.parse_known_args()
    task_name = args.task_id or args.task

    print(f"[START] task={task_name}", flush=True)

    print("Initializing environment...", flush=True)
    
    try:
        state_resp = requests.post(f"{ENV_URL}/reset").json()
    except Exception as e:
        print(f"Error connecting to environment: {e}", flush=True)
        print(f"[END] task={task_name} score=0.0 steps=0", flush=True)
        return

    done = False
    step = 0
    total_current_score = 0.0
    while not done:
        step += 1
        # Prepare prompt with current state
        prompt = f"""
        You are an AI managing a Data Center Cooling System.
        Current State:
        - Rack Temperatures (Goal: get all < 25.0 C): {state_resp['rack_temps']}
        - Fan Speeds (Scale 1-5): {state_resp['fan_speeds']}
        - Total Power (Goal: keep <= 500 W): {state_resp['power_usage']}W
        
        Provide your action as a JSON object with keys: 'fan_change_rack1', 'fan_change_rack2', 'fan_change_rack3'.
        Values must be integers: -1 (decrease speed), 0 (keep speed), or 1 (increase speed).
        """
        
        try:
            # Call Gemini (disguised as an OpenAI call)
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            
            action_str = response.choices[0].message.content
            action = json.loads(action_str)
            print(f"Agent Action: {action}", flush=True)
            
            # Take step in environment
            step_resp = requests.post(f"{ENV_URL}/step", json=action).json()
            
            state_resp = step_resp['state']
            done = step_resp['done']
            
            scores = step_resp.get('scores', {})
            if isinstance(scores, dict):
                score_key = "easy"
                if "medium" in task_name.lower():
                    score_key = "medium"
                elif "hard" in task_name.lower():
                    score_key = "hard"
                current_reward = float(scores.get(score_key, 0.0))
            elif isinstance(scores, (int, float)):
                current_reward = float(scores)
            else:
                current_reward = 0.0
                
            total_current_score += current_reward
            
            print(f"[STEP] step={step} reward={current_reward}", flush=True)
            print(f"Current Scores: {scores}\n", flush=True)
            
            # Pause to prevent rate limits
            time.sleep(8) 
            
        except Exception as e:
            print(f"API Error: {e}", flush=True)
            break

    print(f"[END] task={task_name} score={total_current_score} steps={step}", flush=True)

if __name__ == "__main__":
    run_inference()
