#Ai model for predicting port delay
#import necessary packages
import tensorflow as tf    
import numpy as np
import pandas as pd
import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,LabelEncoder
import matplotlib.pyplot as pt

random.seed(42)
#Reading excel data file
#for your change the path to xlsx folder
data=pd.read_excel(r"S:\projects\ministry of steel project\gitfiles\logistics-optimizer\ai_for_prediction\vessel_delay_history.xlsx")
data=data.drop("Demurrage_Cost(₹)",axis=1)

#Converting string into numerical value
Port_Name_encode=LabelEncoder()
data["Port_Name"]=Port_Name_encode.fit_transform(data["Port_Name"])
Vessel_Name_encode=LabelEncoder()
data["Vessel_Name"]=Vessel_Name_encode.fit_transform(data["Vessel_Name"])

#Converting datatime into seconds as numerical value
data["ETA_Datetime"]=pd.to_datetime(data["ETA_Datetime"]).astype(np.int64)//10**9
data["Actual_Berth_Time"]=pd.to_datetime(data["Actual_Berth_Time"]).astype(np.int64)//10**9
data["Laydays_Start"]=pd.to_datetime(data["Laydays_Start"]).astype(np.int64)//10**9
data["Laydays_End"]=pd.to_datetime(data["Laydays_End"]).astype(np.int64)//10**9

#extracting input and output 
data_input=data.drop("Delay_Hours",axis=1)
data_output=data["Delay_Hours"]



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
    tf.keras.layers.Dense(1)
])

#complie the model
ai_model_1.compile(loss="mse",optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),metrics=["mae"])

#To stop the program if no improvement 
early_stop = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=50, restore_best_weights=True)

#Train the data
ai_model_1.fit(data_input,data_output,epochs=500,verbose=1,shuffle=0,callbacks=[early_stop])

#Saving a mode
#Change path where to save
ai_model_1.save(r"S:\projects\ministry of steel project\gitfiles\logistics-optimizer\ai_for_prediction\port_ai_model.keras")
