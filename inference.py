import os
import requests
import json
import time
from openai import OpenAI

# 1. Point the OpenAI client to Google's Gemini servers!
API_BASE_URL = os.getenv("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")

# We'll hook this up to the powerful Pro model for the best logic
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash") 

# 2. Put your REAL Gemini key right here (starts with AIza...)
GEMINI_API_KEY = os.getenv("HF_TOKEN", "GEMINI_API_KEYS") 

# 3. Your live Hugging Face Space URL
ENV_URL = os.getenv("ENV_URL", "https://rohannk-datacenter-openenv.hf.space")

# We are strictly using the OpenAI client to satisfy the hackathon rules
client = OpenAI(
    base_url=API_BASE_URL, 
    api_key=GEMINI_API_KEY
)

def run_inference():
    print("Initializing environment...")
    
    try:
        state_resp = requests.post(f"{ENV_URL}/reset").json()
    except Exception as e:
        print(f"Error connecting to environment: {e}")
        return
    
    done = False
    while not done:
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
            print(f"Agent Action: {action}")
            
            # Take step in environment
            step_resp = requests.post(f"{ENV_URL}/step", json=action).json()
            
            state_resp = step_resp['state']
            done = step_resp['done']
            print(f"Current Scores: {step_resp['scores']}\n")
            
            # Pause to prevent rate limits
            time.sleep(8) 
            
        except Exception as e:
            print(f"API Error: {e}")
            break

if __name__ == "__main__":
    run_inference()