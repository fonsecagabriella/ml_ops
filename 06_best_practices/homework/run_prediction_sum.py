# ---------------------------------------------------------------------------
# run_prediction_sum.py  (you can name it whatever you like)
# ---------------------------------------------------------------------------
import os, subprocess, math, pickle, pandas as pd
from datetime import datetime
from batch import (
    get_input_path, get_output_path,
    _s3_storage_options, prepare_data             # <- reuse your helpers
)

YEAR, MONTH = 2023, 1

def dt(h, m, s=0):
    return datetime(2023, 1, 1, h, m, s)

def build_fixture():
    rows = [
        (None, None, dt(1, 1), dt(1, 10)),      # 9 min  (filtered because of NA)
        (1,    1,    dt(1, 2), dt(1, 10)),      # 8 min  ✅ survives
        (1,    None, dt(1, 2), dt(1, 2, 59)),   # 59 min (filtered because of NA)
        (3,    4,    dt(1, 2), dt(2, 2, 1)),    # 1441 min (filtered >60 min)
    ]
    cols = [
        "PULocationID", "DOLocationID",
        "tpep_pickup_datetime", "tpep_dropoff_datetime",
    ]
    return pd.DataFrame(rows, columns=cols)

def write_to_localstack(df):
    path = get_input_path(YEAR, MONTH)
    df.to_parquet(
        path,
        engine="pyarrow",
        compression=None,
        index=False,
        storage_options=_s3_storage_options(),
    )
    return path

def run_batch():
    # run the main script exactly like the production job
    res = subprocess.run(
        ["python", "batch.py", str(YEAR), f"{MONTH:02d}"],
        check=True,
        capture_output=True, text=True,
    )
    print(res.stdout)

def fetch_predictions():
    path = get_output_path(YEAR, MONTH)
    df_pred = pd.read_parquet(path, storage_options=_s3_storage_options())
    total = df_pred["predicted_duration"].sum()
    return total

if __name__ == "__main__":
    # 1️⃣  build & upload fixture
    df_fixture = build_fixture()
    write_to_localstack(df_fixture)

    # 2️⃣  run the pipeline
    run_batch()

    # 3️⃣  pull result back & inspect
    total_minutes = fetch_predictions()
    print(f"Sum of predicted durations: {total_minutes:.2f} min")

    # 4️⃣  (optional) turn this into an assertion
    #     by comparing against a *freshly* computed target
    #     so there is no magic constant in the repo
    # --------------------------------------------------------------------
    # If you want a proper test without hard-coding a number, do this:
    # --------------------------------------------------------------------
    # with open("model.bin", "rb") as f:
    #     dv, model = pickle.load(f)
    #
    # df_prep   = prepare_data(df_fixture)
    # X         = dv.transform(df_prep.to_dict("records"))
    # expected  = model.predict(X).sum()
    #
    # assert math.isclose(total_minutes, expected, rel_tol=1e-6), (
    #     f"Pipeline total {total_minutes:.2f} ≠ direct total {expected:.2f}"
    # )

