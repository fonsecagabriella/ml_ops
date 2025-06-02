# MLOps - Best Practices

## How to run tests

- [Notes from 2023](https://github.com/dimzachar/mlops-zoomcamp/blob/master/notes/Week_6/tests.md)

**SUMMARY**
- Create a tests folder
- add __init__.py so Python know it's a package
- create the tests in a file model_test.py. Import the functions you have from the package you want to test. Don't forget the assert in the end.
- to run the tests, run `pipenv run test tests\`