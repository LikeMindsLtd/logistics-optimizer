#import necessay packages
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler,LabelEncoder
from pathlib import Path
import psycopg2 as py



#prediction for port
def predict_port_delay(ai_input:dict):
    #Load our ai model
    ai_model_port=tf.keras.models.load_model((Path(__file__).parent /"ai_models"/"port_ai_model.keras").resolve())
    
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



#prediction for train
def predict_train_delay(ai_input:dict):
    #load ai model
    ai_model_train=tf.keras.models.load_model((Path(__file__).parent /"ai_models"/"train_ai_model.keras").resolve())
    
    #Input from database
    ai_input=pd.DataFrame(ai_input)
    ai_input=ai_input.drop(["Delay_h,Total_Trip_Cost (₹)"],axis=1)

    #Converting string into numerical value
    Trip_ID_encode=LabelEncoder()
    ai_input["Trip_ID"]=Trip_ID_encode.fit_transform(ai_input["Trip_ID"])
    Material_Flow_encode=LabelEncoder()
    ai_input["Material_Flow"]=Material_Flow_encode.fit_transform(ai_input["Material_Flow"])
    Material_encode=LabelEncoder()
    ai_input["Material"]=Material_encode.fit_transform(ai_input["Material"])
    Source_encode=LabelEncoder()
    ai_input["Source"]=Source_encode.fit_transform(ai_input["Source"])
    Destination_encode=LabelEncoder()
    ai_input["Destination"]=Destination_encode.fit_transform(ai_input["Destination"])



    #Converting ai_inputtime into seconds as numerical value
    ai_input["Departure_Time"]=pd.to_datetime(ai_input["Departure_Time"]).astype(np.int64)//10**9
    ai_input["Arrival_Time"]=pd.to_datetime(ai_input["Arrival_Time"]).astype(np.int64)//10**9
    
    #Standarise the input
    scalar=StandardScaler()
    ai_input=scalar.fit_transform(ai_input)
    
    #return the predict
    return ai_model_train.predict(ai_input).flatten()