import tensorflow as tf
import numpy as np
import os
from typing import Dict, List, Any

# --- Global Model and Path Setup ---
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), 
    "..", 
    "ai_models", 
    "train_delay_and_cost.keras"
)
TRAIN_MODEL = None

def _load_train_model():
    """Loads the Keras model once."""
    global TRAIN_MODEL
    if TRAIN_MODEL is None:
        try:
            TRAIN_MODEL = tf.keras.models.load_model(MODEL_PATH)
            print(f"Successfully loaded Train Delay Model from: {MODEL_PATH}")
        except Exception as e:
            # If the model hasn't been trained yet, this is a common failure.
            print(f"WARNING: Train Model failed to load. Run training script. Error: {e}")
            # Set a placeholder to prevent repeated load attempts
            TRAIN_MODEL = "UNLOADED" 

def get_train_delay_and_cost(data: Dict[str, List[Any]]) -> Dict[str, float]:

    
    _load_train_model()

    
    # Define the 15 features the model expects, in the correct order
    INPUT_FEATURES = [
        "quantity_tonnes",
        "distance_km",
        "rake_availability_index",
        "base_time_h",
        "loading_time_h",
        "unloading_time_h",
        "rail_freight_inr_tonne",
        "port_handling_inr_tonne",
        "departure_time_sec",
        "trip_id_encoded",
        "material_flow_encoded",
        "material_encoded",
        "source_encoded",
        "destination_encoded",
        "rake_id_encoded"
    ]
    
    input_values = []
    for key in INPUT_FEATURES:
        # data.get(key, [0])[0] safely gets the first item, or 0 if missing.
        input_values.append(data.get(key, [0])[0])
    
    # Convert to NumPy array for Keras
    input_array = np.array(input_values, dtype=np.float32).reshape(1, -1)

    if TRAIN_MODEL == "UNLOADED":
        # Return a safe, hardcoded default if the model failed to load
        print("Using simulated default prediction for Train.")
        return {
            "train_delay_hours": 8.0,
            "train_cost": 450.0
        }

    # --- Prediction ---
    try:

        prediction = TRAIN_MODEL.predict(input_array, verbose=0)
        
        # The model outputs an array of 2 values: [delay_h, total_trip_cost_inr]
        return {
            "train_delay_hours": float(prediction[0][0]),
            "train_cost": float(prediction[0][1])
        }
    except Exception as e:
        print(f"Train Model prediction runtime error: {e}. Returning safe defaults.")
        return {
            "train_delay_hours": 9.5,
            "train_cost": 500.0
        }