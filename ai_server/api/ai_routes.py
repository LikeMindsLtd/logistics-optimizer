from flask import Blueprint, request, jsonify
from ..services.ai_service import trigger_training, get_training_status, get_port_prediction, get_train_prediction

bp = Blueprint("ai_api", __name__, url_prefix="/api/ai/v1")

# ---------------- Training Route ----------------
@bp.route("/trigger-training", methods=["POST"])
def start_training():

    result = trigger_training()
    return jsonify(result), 202


@bp.route("/training-status", methods=["GET"])
def training_status():
    return jsonify(get_training_status())


# ---------------- Port Delay Prediction ----------------
@bp.route("/port/predict", methods=["POST"])
def port_predict():

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    result = get_port_prediction(data)
    status = 200 if "prediction" in result else 500
    return jsonify(result), status


# ---------------- Train Delay Prediction ----------------
@bp.route("/train/predict", methods=["POST"])
def train_predict():

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    result = get_train_prediction(data)
    status = 200 if "prediction" in result else 500
    return jsonify(result), status
