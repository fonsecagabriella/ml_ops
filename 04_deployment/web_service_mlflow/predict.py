import os
import mlflow
from flask import Flask, request, jsonify

##############################################################################
# 1. Where is the MLflow tracking server?
##############################################################################
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",         # e.g. "http://host.docker.internal:5001"
    "http://host.docker.internal:5001"
)
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

##############################################################################
# 2. Which run contains the model we want to serve?
##############################################################################
RUN_ID = os.getenv(
    "RUN_ID",                      # pass with -e RUN_ID=<your_run_id>
    "0c16299ef4c245cfada99d0be9966204"
)

logged_model_uri = f"runs:/{RUN_ID}/model"
model = mlflow.pyfunc.load_model(logged_model_uri)

##############################################################################
# 3. Flask inference service
##############################################################################
def prepare_features(ride):
    return {
        "PU_DO": f"{ride['PULocationID']}_{ride['DOLocationID']}",
        "trip_distance": ride["trip_distance"],
    }

def predict_single(ride):
    features = prepare_features(ride)
    # pipeline expects a list/array-like of dicts
    preds = model.predict([features])
    return float(preds[0])

app = Flask("duration-prediction")

@app.route("/predict", methods=["POST"])
def predict_endpoint():
    ride = request.get_json()
    duration = predict_single(ride)
    return jsonify({"duration": duration, "model_version": RUN_ID})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9696, debug=False)
