from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your transformation logic here

    # Convert categorical columns to dict format
    train_dicts = data[['PULocationID', 'DOLocationID']].to_dict(orient='records')

    # Vectorize
    dv = DictVectorizer()
    X_train = dv.fit_transform(train_dicts)

    # Target variable
    y_train = data['duration'].values

    # Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    print(f"Intercept: {model.intercept_:.2f}")

    return dv, model


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'