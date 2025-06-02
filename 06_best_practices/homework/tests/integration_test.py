# tests/integration_test.py
import os
import pandas as pd
from datetime import datetime
from batch import _s3_storage_options, get_input_path   # reuse helpers

def dt(h, m, s=0):
    return datetime(2023, 1, 1, h, m, s)

def create_test_dataframe():
    """Exactly the same rows you used in the unit test (Q3)."""
    data = [
        (None, None, dt(1, 1),  dt(1, 10)),   # 9  mins
        (1,    1,    dt(1, 2),  dt(1, 10)),   # 8  mins
        (1,    None, dt(1, 2),  dt(1, 2, 59)),# 59 mins
        (3,    4,    dt(1, 2),  dt(2, 2, 1)), # 1441 mins
    ]
    cols = ['PULocationID', 'DOLocationID',
            'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    return pd.DataFrame(data, columns=cols)

def main():
    df_input = create_test_dataframe()

    # We pretend this file is “January 2023”
    year, month = 2023, 1
    input_file = get_input_path(year, month)          # s3://nyc-duration/in/2023-01.parquet
    opts        = _s3_storage_options()               # points pandas → Localstack

    # ---- SAVE to Localstack -------------------------------------------------
    df_input.to_parquet(
        input_file,
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=opts
    )
    print(f"✅  Written test data to {input_file}")

    # ---- QUICK SIZE CHECK (not strictly part of the integration test) ------
    # Use boto3 via s3fs or just shell out; here’s the simple shell variant:
    size = int(os.popen(f"aws --endpoint-url {os.environ['S3_ENDPOINT_URL']} "
                        f"s3 ls {input_file}").read().split()[2])
    print(f"Object size in bytes: {size}")

if __name__ == "__main__":
    main()
