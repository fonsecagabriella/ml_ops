import pickle
import pandas as pd
import os
import argparse

output_dir = "data" # directory to save the predictions
os.makedirs(output_dir, exist_ok=True)  # ensure the directory exists

categorical = ['PULocationID', 'DOLocationID']


def read_data(filename,  year, month):
    df = pd.read_parquet(filename)

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')

    # this line is needed for question 2
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    return df

def save_predictions(predictions, df, year:int, month:int):
    # homework - question 02
    # Next, write the ride id and the predictions to a dataframe with results.
    df_results = pd.DataFrame({
        'ride_id': df['ride_id'],
        'prediction': predictions
    })

    # Save the results to a parquet file
    output_file = os.path.join(output_dir, f"predictions__{year:04d}-{month:02d}.parquet")


    df_results.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )

    # Get and print file size
    file_size = os.path.getsize(output_file)
    print(f"Predictions saved to: {output_file}")
    print(f"File size: {file_size/1024/1024:.2f} MB")

def main(year: int, month: int) -> None:
    with open('model.bin', 'rb') as f_in:
        dv, model = pickle.load(f_in)


    df = read_data(f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet', year, month)


    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)

    print(f'Standard deviation of predictions: {y_pred.std():.2f}')
    print(f'Mean of predictions: {y_pred.mean():.2f}')

    save_predictions(y_pred, df, year, month)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run NYC yellow-cab prediction for a given year/month"
    )
    parser.add_argument("--year",  type=int, required=True, help="4-digit year (e.g. 2023)")
    parser.add_argument("--month", type=int, required=True, choices=range(1, 13),
                        metavar="[1-12]", help="Month number")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args.year, args.month)