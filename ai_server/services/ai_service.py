from ..predictors.predict_port_delay import predict_port_delay
from ..predictors.predict_train_delay import predict_train_delay
import subprocess
import threading
import os
import sys

# Global status dict
training_status = {
    "status": "idle",
    "message": "",
    "errors": ""
}


# ---------------- Training Function ----------------

def run_training_script():
    global training_status
    training_status["status"] = "running"
    training_status["message"] = "Training started..."
    training_status["errors"] = {}

    scripts = {
        "train_delay": os.path.join(os.path.dirname(__file__), "..", "training_scripts", "train_train_delay_model.py"),
        "port_delay": os.path.join(os.path.dirname(__file__), "..", "training_scripts", "train_port_delay_model.py")
    }

    for name, path in scripts.items():
        try:
            subprocess.run([sys.executable, path], check=True)
            training_status["errors"][name] = "success"
        except subprocess.CalledProcessError as e:
            training_status["errors"][name] = str(e)

    # Final status
    if any(v != "success" for v in training_status["errors"].values()):
        training_status["status"] = "failed"
        training_status["message"] = "One or more scripts failed"
    else:
        training_status["status"] = "success"
        training_status["message"] = "All training scripts completed successfully"


def trigger_training():

    thread = threading.Thread(target=run_training_script, daemon=True)
    thread.start()
    return {"message": "Training started"}

def get_training_status():
    return training_status



# ---------------- Prediction Functions ----------------

def get_port_prediction(data: dict):

    try:
        prediction = predict_port_delay(data)
        return {"prediction": prediction.tolist()}
    except Exception as e:
        return {"error": str(e)}

def get_train_prediction(data: dict):

    try:
        prediction = predict_train_delay(data)
        return {"prediction": prediction.tolist()}
    except Exception as e:
        return {"error": str(e)}
