import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # only errors, suppress warnings/info
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler,LabelEncoder
from pathlib import Path


def predict_port_delay(ai_input:dict):
    #Load our ai model
    ai_model_port=tf.keras.models.load_model((Path(__file__).parent.parent /"ai_models"/"port_ai_model.keras").resolve())
    
    #Read from ai_inputbase
    #ai_input=pd.read_sql_query("SELECT * FROM vessel_delay_history ORDER BY ctid DESC LIMIT 1")
    ai_input=pd.DataFrame(ai_input)
    ai_input=ai_input.drop(["Delay_Hours","Demurrage_Cost(₹)"],axis=1)


    #Converting date and time into integer millisecons
    ai_input["ETA_DateTime"]=pd.to_datetime(ai_input["ETA_DateTime"]).astype(np.int64)//10**9
    ai_input["Laydays_Start"]=pd.to_datetime(ai_input["Laydays_Start"]).astype(np.int64)//10**9
    ai_input["Laydays_End"]=pd.to_datetime(ai_input["Laydays_End"]).astype(np.int64)//10**9


    #Converting string into integer
    input_Port_Name_encode=LabelEncoder()
    ai_input["Port_Name"]=input_Port_Name_encode.fit_transform(ai_input["Port_Name"])

    input_Vessel_Name_encode=LabelEncoder()
    ai_input["Vessel_Name"]=input_Vessel_Name_encode.fit_transform(ai_input["Vessel_Name"])

    #Standarise the input
    scalar=StandardScaler()
    ai_input=scalar.fit_transform(ai_input)


    return ai_model_port.predict(ai_input).flatten()