import subprocess
import threading
import os
import sys
import datetime
from typing import Dict, Any, List, Union

from ..predictors.port_predictor import get_port_delay_and_cost
from ..predictors.train_predictor import get_train_delay_and_cost


# Global status dict for training status
training_status = {
    "status": "idle",
    "message": "",
    "errors": ""
}

# --- 1. Training Functions ---

def run_training_script():
    """Runs all training scripts in a subprocess."""
    global training_status
    training_status["status"] = "running"
    training_status["message"] = "Training started..."
    training_status["errors"] = {}

    scripts = {
        "train_delay": os.path.join(os.path.dirname(__file__), "..", "training_scripts", "train_train_delay_model.py"),
        "port_delay": os.path.join(os.path.dirname(__file__), "..", "training_scripts", "train_port_delay_model.py")
    }

    for name, path in scripts.items():
        print(f"Starting training for {name} using script: {path}")
        try:
            # Using sys.executable ensures the script is run with the same Python environment
            result = subprocess.run([sys.executable, path], check=True)
            training_status["errors"][name] = "success"
            print(f"Training {name} finished successfully.")
        except subprocess.CalledProcessError as e:
            training_status["errors"][name] = f"Script failed with exit code {e.returncode}. Stderr: {e.stderr.strip()}"
            print(f"Training {name} FAILED. Error: {e.stderr.strip()}")
        except FileNotFoundError:
             training_status["errors"][name] = f"Training script not found at {path}"
             print(f"Training {name} FAILED. Script not found.")


    # Final status check
    if any(v != "success" for v in training_status["errors"].values()):
        training_status["status"] = "failed"
        training_status["message"] = "One or more scripts failed. Check 'errors' for details."
    else:
        training_status["status"] = "success"
        training_status["message"] = "All training scripts completed successfully."


def trigger_training():
    """Starts the training process in a background thread."""
    # Only allow training if currently idle
    if training_status["status"] != "running":
        thread = threading.Thread(target=run_training_script, daemon=True)
        thread.start()
        return {"message": "Training started in background."}
    else:
        return {"message": "Training is already running."}

def get_training_status():
    """Returns the current status of the training process."""
    return training_status


# --- 2. Prediction Functions (Direct Wrappers) ---

def get_port_prediction(data: dict) -> Dict[str, Any]:
    """Wrapper for port delay/cost prediction."""
    try:
        prediction = get_port_delay_and_cost(data)
        # FIX: Return the prediction dict directly
        return prediction 
    except Exception as e:
        return {"error": str(e)}

def get_train_prediction(data: dict) -> Dict[str, Any]:
    """Wrapper for train delay/cost prediction."""
    try:
        prediction = get_train_delay_and_cost(data)
        # FIX: Return the prediction dict directly
        return prediction
    except Exception as e:
        return {"error": str(e)}

# --- 3. Combined AI Prediction for Optimizer ---

def ai_model_delay(starting_point: str, ending_point: str, date: datetime.date, tons: int) -> tuple[Dict[str, float], Dict[str, float]]:
    """
    Combines input preparation and calls to all required AI predictors.
    It returns two dictionaries: port_ai_output and plant_ai_output (which is the rail/train output).
    """

    # --- Data Preparation & Feature Engineering (Simulated Encoding/Conversion) ---

    # Convert date to timestamp (sec since epoch) for the models (8 AM UTC placeholder)
    departure_dt = datetime.datetime.combine(date, datetime.time(8, 0), tzinfo=datetime.timezone.utc)
    departure_time_sec = int(departure_dt.timestamp())

    # 1. Port Model Input (Vessel Delay at Port/Ending Point)
    port_input = {
        # Raw Input features needed by the predictor
        "port_name": [ending_point], 
        "vessel_name": ["DummyVessel1"],
        "eta_datetime_sec": [departure_time_sec],
        "parcel_size_tonnes": [float(tons)],
        "queue_length": [10],
        "weather_score": [0.8],
        # Simulated Encoded/Converted Features (Needed for model compatibility)
        "port_name_encoded": [1],
        "vessel_name_encoded": [5],
    }
    
    # 2. Train Model Input (Rail Leg Delay/Cost)
    train_input = {
        # Raw Input features (Tons/Distance)
        "quantity_tonnes": [float(tons)],
        "distance_km": [850.0], 
        "departure_time_sec": [departure_time_sec],
        
        # Simulated Encoded/Converted Features 
        "trip_id_encoded": [101], 
        "material_flow_encoded": [2],
        "material_encoded": [3],
        "source_encoded": [starting_point],
        "destination_encoded": [ending_point],
        "rake_id_encoded": [42],
        
        # Other required numerical features (fixed for simulation)
        "rake_availability_index": [0.95],
        "base_time_h": [10.0],
        "loading_time_h": [5.0],
        "unloading_time_h": [5.0],
        "rail_freight_inr_tonne": [1500.0],
        "port_handling_inr_tonne": [50.0],
    }
    
    # --- Call Predictors ---
    try:
        # Port Prediction
        port_model_output = get_port_delay_and_cost(port_input)
        if "error" in port_model_output:
            raise Exception(f"Port prediction failed: {port_model_output['error']}")
            
        # Train Prediction (Used for the 'plant_ai' portion in the optimizer logic)
        train_model_output = get_train_delay_and_cost(train_input) 

        if "error" in train_model_output:
            raise Exception(f"Train prediction failed: {train_model_output['error']}")
            
    except Exception as e:
        # Global fallback: If any AI model fails, return a safe default
        print(f"FATAL: One or more AI Prediction calls failed: {e}. Returning safe defaults.")
        safe_port = {"port_delay_hours": 10.0, "port_cost": 350.0}
        safe_train = {"plant_delay_hours": 15.0, "plant_cost": 500.0}
        return safe_port, safe_train 

    # Return the two dictionaries the optimizer expects
    return port_model_output, train_model_output
