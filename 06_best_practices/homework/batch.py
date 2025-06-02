#!/usr/bin/env python
# coding: utf-8

import sys
import os
import pickle
import pandas as pd


def _s3_storage_options():
    """
    Return a dict for pandas/s3fs that points to Localstack
    whenever S3_ENDPOINT_URL is set.
    """
    endpoint = os.getenv("S3_ENDPOINT_URL")        # e.g. http://localhost:4566
    if not endpoint:                               # fall back to real AWS
        return None
    return {"client_kwargs": {"endpoint_url": endpoint}}


def read_data(filename):
    opts = _s3_storage_options()

    df = pd.read_parquet(filename, storage_options=opts)

    return df


def get_input_path(year: int, month: int):
    default_input_pattern = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    return input_pattern.format(year=year, month=month)


def get_output_path(year: int, month: int):
    default_output_pattern = 's3://nyc-duration-prediction-alexey/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet'
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)



def prepare_data(df, categorical):
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')

    return df

def save_data(df: pd.DataFrame, path: str) -> None:
    """
    Write a parquet file either to real S3 or to Localstack,
    depending on whether $S3_ENDPOINT_URL is set.
    """
    opts = _s3_storage_options()
    df.to_parquet(path, engine="pyarrow", index=False, storage_options=opts)



def main(year:int, month:int):


    #input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    #output_file = f'output/yellow_tripdata_{year:04d}-{month:02d}.parquet'

    # added to question 5, localstack
    input_file = get_input_path(year, month)
    output_file = get_output_path(year, month)



    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)


    categorical = ['PULocationID', 'DOLocationID']

    df = read_data(input_file)
    df = prepare_data(df, categorical)

    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')


    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    print('predicted mean duration:', y_pred.mean())

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred


    #opts = _s3_storage_options()
    #df_result.to_parquet(output_file, engine='pyarrow', index=False, storage_options=opts)

    # question 6, save to localstack
    save_data(df_result, output_file)


if __name__ == "__main__":
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    main(year, month)