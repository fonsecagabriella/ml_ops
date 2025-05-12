import requests
import pandas as pd
from io import BytesIO

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your data loading logic here

    year="2023"
    month="03"

    url = (
        'https://d37ci6vzurychx.cloudfront.net/trip-data/'
        f'yellow_tripdata_{year}-{month}.parquet'
    )
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request succeeded
    df = pd.read_parquet(BytesIO(response.content))
    
    print(f"Loaded {len(df):,} rows from {url}")
    
    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'