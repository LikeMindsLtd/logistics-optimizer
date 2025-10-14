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
response = requests.get("http://localhost:5000/api/main/v1/data/delay_history")
data_json=response.json()
data=pd.DataFrame(data_json)

#Converting string into numerical value
Port_Name_encode=LabelEncoder()
data["port_name"]=Port_Name_encode.fit_transform(data["port_name"])
Vessel_Name_encode=LabelEncoder()
data["vessel_name"]=Vessel_Name_encode.fit_transform(data["vessel_name"])

#Converting datatime into seconds as numerical value
data["eta_datetime"]=pd.to_datetime(data["eta_datetime"]).astype(np.int64)//10**9
data["laydays_start"]=pd.to_datetime(data["laydays_start"]).astype(np.int64)//10**9
data["laydays_end"]=pd.to_datetime(data["laydays_end"]).astype(np.int64)//10**9

#extracting input and output 
data_input=data.drop(["delay_hours","demurrage_cost_inr","actual_berth_time","past_delay_avg_hours","laydays_limit_hours"],axis=1)
data_output=data[["delay_hours","demurrage_cost_inr"]]



#standarise the input
scalar=StandardScaler()
data_input=scalar.fit_transform(data_input)

#separating data for training model and test model
#data_input_train,data_input_test,data_output_train,data_output_test=train_test_split(data_std_input,data_output,test_size=0.5,random_state=42)

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

model_path = os.path.join(model_dir, "train_ai_model.keras")
ai_model_1.save(model_path)
print(f"Model saved at: {model_path}")

