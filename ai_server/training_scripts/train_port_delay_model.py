import tensorflow as tf
import numpy as np
import pandas as pd
import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import requests
import os

random.seed(42)
np.random.seed(42)
tf.random.set_seed(42)

# --- 1. Data Fetching ---
# Request to database 
try:
    response = requests.get("http://localhost:5000/api/main/v1/data/vessel_delay_history")
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

# Converting string into numerical value using LabelEncoder
Port_Name_encode = LabelEncoder()
data["port_name_encoded"] = Port_Name_encode.fit_transform(data["port_name"])
Vessel_Name_encode = LabelEncoder()
data["vessel_name_encoded"] = Vessel_Name_encode.fit_transform(data["vessel_name"])

# Converting datetime into numerical value (seconds since epoch)
data["eta_datetime_sec"] = pd.to_datetime(data["eta_datetime"], utc=True).astype(np.int64) // 10**9
data["laydays_start_sec"] = pd.to_datetime(data["laydays_start"], utc=True).astype(np.int64) // 10**9
data["laydays_end_sec"] = pd.to_datetime(data["laydays_end"], utc=True).astype(np.int64) // 10**9

# --- 3. Extracting Input and Output ---

# Features used for prediction (Input X)
features = [
    "id", 
    "port_name_encoded", 
    "vessel_name_encoded",
    "eta_datetime_sec", 
    "parcel_size_tonnes",
    "laydays_start_sec", 
    "laydays_end_sec",
    "queue_length",
    "weather_score",
    "crane_availability",
    "past_delay_avg_hours",
    "laydays_limit_hours"
]

# Output (Target Y)
targets = ["delay_hours", "demurrage_cost_inr"]

# Clean the input features (remove original string/datetime columns and the target columns)
X = data[features].copy()
y = data[targets].copy()

# The original code dropped columns from 'data'. Replicating the features list based on the original drop:
# data_input = data.drop(["delay_hours","demurrage_cost_inr","actual_berth_time","past_delay_avg_hours","laydays_limit_hours"],axis=1)

X = data.drop([
    "delay_hours", 
    "demurrage_cost_inr", 
    "actual_berth_time", 
    "past_delay_avg_hours", 
    "laydays_limit_hours",
    "port_name", 
    "vessel_name",
    "eta_datetime", 
    "laydays_start", 
    "laydays_end"
], axis=1)

# Ensure the columns align with what the original script expected before the manual drops:
# X should now contain: id, parcel_size_tonnes, queue_length, weather_score, crane_availability, 
# and the newly encoded/converted columns: port_name_encoded, vessel_name_encoded, eta_datetime_sec, laydays_start_sec, laydays_end_sec

# --- 4. Standardization and Splitting ---

# Standardize the input features
scalar = StandardScaler()
X_scaled = scalar.fit_transform(X)

# Separating data for training and testing (50% test size is usually high, but kept if desired)
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, 
    y, 
    test_size=0.3, # Changed to 30% test size (more common)
    random_state=42
)

# --- 5. Model Definition and Training ---

# Creating model
ai_model_1 = tf.keras.models.Sequential([
    tf.keras.layers.Dense(100, activation="relu", input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(80, activation="relu"),
    tf.keras.layers.Dense(50, activation="relu"),
    tf.keras.layers.Dense(30, activation="relu"),
    tf.keras.layers.Dense(2) # Output layer with 2 units for 'delay_hours' and 'demurrage_cost_inr'
])

# Compile the model
ai_model_1.compile(
    loss="mse",
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    metrics=["mae"]
)

# To stop the program if no improvement 
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss', # Use validation loss for early stopping if test data is used
    patience=50, 
    restore_best_weights=True
)

# Train the data
print("Starting model training...")
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

model_path = os.path.join(model_dir, "vessel_delay_model.keras")
ai_model_1.save(model_path)
print(f"Model saved at: {model_path}")