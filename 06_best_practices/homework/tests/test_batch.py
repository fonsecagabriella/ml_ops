import pandas as pd
from datetime import datetime
from batch import prepare_data  


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


def test_prepare_data():
    data = [
        (None, None, dt(1, 1), dt(1, 10)),     # 9 mins, but missing locations
        (1, 1, dt(1, 2), dt(1, 10)),           # 8 mins, valid
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),  # 59 mins, missing location
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      # 1441 mins, invalid (>60)
    ]

    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df = pd.DataFrame(data, columns=columns)

    categorical = ['PULocationID', 'DOLocationID']
    result = prepare_data(df, categorical)

    # Only the 2nd row has complete data and duration within bounds
    expected_data = {
        'PULocationID': ['1'],
        'DOLocationID': ['1'],
        'tpep_pickup_datetime': [dt(1, 2)],
        'tpep_dropoff_datetime': [dt(1, 10)],
        'duration': [8.0]
    }
    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_df.reset_index(drop=True))
