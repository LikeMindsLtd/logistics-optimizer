import tensorflow as tf
import numpy as np
import pandas as pd
import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import requests
import os

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)
tf.random.set_seed(42)

# --- 1. Data Fetching ---
# Ensure the table name 'trains' is correct as per your Flask routes.py
try:
    response = requests.get("http://localhost:5000/api/main/v1/data/trains")
    response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    data_json = response.json().get('data', [])
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from API: {e}")
    exit()

if not data_json:
    print("Error: No data retrieved from API. Cannot train model.")
    exit()

data = pd.DataFrame(data_json)

# --- 2. Feature Engineering & Encoding ---

# Columns to encode
ENCODE_COLUMNS = ["trip_id", "material_flow", "material", "source", "destination", "rake_id"]
label_encoders = {}

for col in ENCODE_COLUMNS:
    # Handle cases where column might not exist or contains NaNs
    if col in data.columns and not data[col].isnull().all():
        le = LabelEncoder()
        # Convert to string to ensure fit_transform handles mixed types correctly
        data[f"{col}_encoded"] = le.fit_transform(data[col].astype(str))
        label_encoders[col] = le
    else:
        # If column is missing or all NaN, fill with a placeholder encoder
        data[f"{col}_encoded"] = 0 # Or a single category

# Converting datetime into numerical value (seconds since epoch)
# 'arrival_time' is a FUTURE feature and MUST be removed for prediction
data["departure_time_sec"] = pd.to_datetime(data["departure_time"], utc=True).astype(np.int64) // 10**9
# data["arrival_time_sec"] = pd.to_datetime(data["arrival_time"], utc=True).astype(np.int64) // 10**9

# --- 3. Extracting Input and Output ---

# Features used for prediction (Input X)
# IMPORTANT: 'arrival_time' and related calculated fields like 'total_time_h' are removed
# as they are only known AFTER the event being predicted ('delay_h').
INPUT_COLUMNS = [
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

# Output (Target Y)
TARGET_COLUMNS = ["delay_h", "total_trip_cost_inr"]

# Select only the columns needed, ensuring they exist after encoding/conversion
# This helps prevent KeyError if an optional column is missing.
X = data[[col for col in INPUT_COLUMNS if col in data.columns]].copy()
y = data[TARGET_COLUMNS].copy()

# Fill any remaining NaN values (e.g., from optional columns) with 0 or mean
X = X.fillna(0)

# --- 4. Standardization and Splitting ---

# Standardize the input features
scalar = StandardScaler()
X_scaled = scalar.fit_transform(X)

# Separating data for training and testing
# Using 30% for testing is common for validation
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, 
    y, 
    test_size=0.3,
    random_state=42
)

# --- 5. Model Definition and Training ---

# Creating model
ai_model_1 = tf.keras.models.Sequential([
    tf.keras.layers.Dense(100, activation="relu", input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(80, activation="relu"),
    tf.keras.layers.Dense(50, activation="relu"),
    tf.keras.layers.Dense(30, activation="relu"),
    tf.keras.layers.Dense(2) # Output layer with 2 units for 'delay_h' and 'total_trip_cost_inr'
])

# Compile the model
ai_model_1.compile(
    loss="mse",
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    metrics=["mae"]
)

# To stop the program if no improvement (using val_loss for robust stopping)
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss', 
    patience=50, 
    restore_best_weights=True
)

# Train the data
print("Starting model training for train delays and cost...")
ai_model_1.fit(
    X_train,
    y_train,
    epochs=500,
    validation_data=(X_test, y_test), # Use the test set for validation during training
    verbose=2, # Show training progress every epoch
    shuffle=True, 
    callbacks=[early_stop]
)
print("Model training complete.")

# --- 6. Model Saving ---

model_dir = os.path.join(os.path.dirname(__file__), "..", "ai_models") 
os.makedirs(model_dir, exist_ok=True)

# Renaming the model path for clarity
model_path = os.path.join(model_dir, "train_delay_and_cost_model.keras") 
ai_model_1.save(model_path)
print(f"Model saved at: {model_path}")