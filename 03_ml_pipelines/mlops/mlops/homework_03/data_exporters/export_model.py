import mlflow
import pickle
import os

TRACKING_URI = "http://mlflow:5001"
EXPERIMENT_NAME = 'homework-03'

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.set_tag("developer", "gabi")
mlflow.sklearn.autolog()

dest_path = "./models/encoder.b"
os.makedirs(dest_path, exist_ok=True)

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    # Specify your data exporting logic here
    # save the model with mlflow

    try:
        mlflow.end_run()
    except Exception:
        pass

    with mlflow.start_run():

        with open(os.path.join(dest_path, "preprocessor.b"), "wb") as f_out:
            pickle.dump(data[0], f_out) #data[0] is the dictVectorizer

        mlflow.log_artifact(os.path.join(dest_path, "preprocessor.b"), artifact_path="preprocessor")

        mlflow.sklearn.log_model(
            sk_model=data[1], #data[1] is the model
            artifact_path="sklearn-model",
            registered_model_name="linear-reg-model",
        )



