#Ai model for predicting port delay
#import necessary packages
import tensorflow as tf    
import numpy as np
import pandas as pd
import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,LabelEncoder
import matplotlib.pyplot as pt
from pathlib import Path
import psycopg2 as py
import requests

random.seed(42)
#Request to database 
response = requests.get("http://<server-ip>:5000/vessel_data")
data_json=response.json()
data=pd.DataFrame(data_json)

#Converting string into numerical value
Trip_ID_encode=LabelEncoder()
data["Trip_ID"]=Trip_ID_encode.fit_transform(data["Trip_ID"])
Material_Flow_encode=LabelEncoder()
data["Material_Flow"]=Material_Flow_encode.fit_transform(data["Material_Flow"])
Material_encode=LabelEncoder()
data["Material"]=Material_encode.fit_transform(data["Material"])
Source_encode=LabelEncoder()
data["Source"]=Source_encode.fit_transform(data["Source"])
Destination_encode=LabelEncoder()
data["Destination"]=Destination_encode.fit_transform(data["Destination"])



#Converting datatime into seconds as numerical value
data["Departure_Time"]=pd.to_datetime(data["Departure_Time"]).astype(np.int64)//10**9
data["Arrival_Time"]=pd.to_datetime(data["Arrival_Time"]).astype(np.int64)//10**9

#extracting input and output 
data_input=data.drop(["Delay_h","Total_Trip_Cost (₹)","Rake_Availability_Index","Base_Time_h","Loading_Time_h","Unloading_Time_h","Total_Time_h","Arrival_Time"],axis=1)
data_output=data[["Delay_h","Total_Trip_Cost (₹)"]]



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
ai_model_1.fit(data_input,data_output,epochs=500,verbose=1,shuffle=0,callbacks=[early_stop])

#Saving a mode
#Change path where to save
ai_model_1.save("train_ai_model.keras")
