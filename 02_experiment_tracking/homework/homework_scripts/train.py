import os
import pickle
import click

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error

import mlflow


def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


@click.command()
@click.option(
    "--data_path",
    default="./../output",
    help="Location where the processed NYC taxi trip data was saved"
)

def run_train(data_path: str):

    mlflow.set_tracking_uri("sqlite:////Users/gabi/codes/ml_ops/02_experiment_tracking/mlflow-examples/mlflow.db")
    
    mlflow.set_experiment("homework_week_2")

    mlflow.sklearn.autolog()

    with mlflow.start_run():

        X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
        X_val, y_val = load_pickle(os.path.join(data_path, "val.pkl"))

        rf = RandomForestRegressor(max_depth=10, random_state=0)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_val)

        rmse = root_mean_squared_error(y_val, y_pred)

if __name__ == '__main__':
    run_train()
