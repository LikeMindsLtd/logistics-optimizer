import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # only errors, suppress warnings/info
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler,LabelEncoder
from pathlib import Path


def predict_train_delay(ai_input:dict):
    #load ai model
    ai_model_train=tf.keras.models.load_model((Path(__file__).parent.parent /"ai_models"/"train_ai_model.keras").resolve())
    
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