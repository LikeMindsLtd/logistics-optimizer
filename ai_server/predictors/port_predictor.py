import tensorflow as tf
import numpy as np
import pandas as pd
import os
from typing import Dict, List, Any

# --- Global Model and Path Setup ---
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), 
    "..", 
    "ai_models", 
    "vessel_delay_model.keras"
)
PORT_MODEL = None

def _load_port_model():
    """Loads the Keras model once."""
    global PORT_MODEL
    if PORT_MODEL is None:
        try:
            # Note: We must explicitly handle custom objects if the model was complex.
            PORT_MODEL = tf.keras.models.load_model(MODEL_PATH)
            print(f"Successfully loaded Port Delay Model from: {MODEL_PATH}")
        except Exception as e:
            # If the model hasn't been trained yet, this is a common failure.
            print(f"WARNING: Port Model failed to load. Run training script. Error: {e}")
            # Set a placeholder to prevent repeated load attempts
            PORT_MODEL = "UNLOADED" 

def get_port_delay_and_cost(data: Dict[str, List[Any]]) -> Dict[str, float]:
    
    _load_port_model()
    
    # Define the 10 features the model expects, in the correct order
    INPUT_FEATURES = [
        "id", 
        "parcel_size_tonnes",
        "queue_length",
        "weather_score",
        "crane_availability",
        "port_name_encoded",
        "vessel_name_encoded",
        "eta_datetime_sec", 
        "laydays_start_sec", 
        "laydays_end_sec"
    ]
    
    try:
        input_values = [data[key][0] for key in INPUT_FEATURES]
    except KeyError as e:
        raise ValueError(f"Missing required feature for Port Model: {e}. Check input data keys.")

    # Convert to NumPy array for Keras
    input_array = np.array(input_values, dtype=np.float32).reshape(1, -1)

    if PORT_MODEL == "UNLOADED":
        # Return a safe, hardcoded default if the model failed to load
        print("Using simulated default prediction for Port.")
        return {
            "port_delay_hours": 10.0,
            "port_cost": 350.0
        }

    # --- Prediction ---
    try:
        prediction = PORT_MODEL.predict(input_array)
        
        # The model outputs an array of 2 values: [delay_hours, demurrage_cost_inr]
        return {
            "port_delay_hours": float(prediction[0][0]),
            "port_cost": float(prediction[0][1])
        }
    except Exception as e:
        print(f"Port Model prediction runtime error: {e}. Returning safe defaults.")
        return {
            "port_delay_hours": 12.0,
            "port_cost": 400.0
        }
