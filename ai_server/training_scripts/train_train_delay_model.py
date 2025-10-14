import tensorflow as tf    
import numpy as np
import pandas as pd
import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,LabelEncoder
import requests
import os

random.seed(42)
#Request to database 
response = requests.get("http://localhost:5000/api/main/v1/data/trains")
data_json=response.json()
data=pd.DataFrame(data_json)

#Converting string into numerical value
Trip_ID_encode=LabelEncoder()
data["trip_id"]=Trip_ID_encode.fit_transform(data["trip_id"])
Material_Flow_encode=LabelEncoder()
data["material_flow"]=Material_Flow_encode.fit_transform(data["material_flow"])
Material_encode=LabelEncoder()
data["material"]=Material_encode.fit_transform(data["material"])
Source_encode=LabelEncoder()
data["source"]=Source_encode.fit_transform(data["source"])
Destination_encode=LabelEncoder()
data["destination"]=Destination_encode.fit_transform(data["destination"])



#Converting datatime into seconds as numerical value
data["departure_time"]=pd.to_datetime(data["departure_time"]).astype(np.int64)//10**9
data["arrival_time"]=pd.to_datetime(data["arrival_time"]).astype(np.int64)//10**9

#extracting input and output 
data_input=data.drop(["delay_h","total_trip_cost_inr","rake_availability_index","base_time_h","loading_time_h","unloading_time_h","total_time_h","arrival_Time"],axis=1)
data_output=data[["delay_h","total_trip_cost_inr"]]



#standarise the input
scalar=StandardScaler()
data_input=scalar.fit_transform(data_input)


#Creating model
ai_model_1=tf.keras.models.Sequential([
    tf.keras.layers.Dense(100,activation="relu",input_shape=(data_input.shape[1],)),
    tf.keras.layers.Dense(80,activation="relu"),
    tf.keras.layers.Dense(50,activation="relu"),
    tf.keras.layers.Dense(30,activation="relu"),
    tf.keras.layers.Dense(2)
])

#complie the model
ai_model_1.compile(loss="mse",optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),metrics=["mae"])

#To stop the program if no improvement 
early_stop = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=50, restore_best_weights=True)

#Train the data
ai_model_1.fit(data_input,data_output,epochs=500,verbose=0,shuffle=0,callbacks=[early_stop])

model_dir = os.path.join("..", "ai_models")  # relative to model_generators/
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, "port_ai_model.keras")
ai_model_1.save(model_path)
print(f"Model saved at: {model_path}")
