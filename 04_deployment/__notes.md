# Deployment

## 📚 Index

1. [Key Insights](#key-insights)  
   - [Batch Mode Deployment](#️-batch-mode-deployment)  
   - [Web Service Deployment](#-web-service-deployment)  
   - [Streaming Architecture](#-streaming-architecture)  
   - [Scalability of Streaming Models](#️-scalability-of-streaming-models)  
   - [Cost Implications of Deployment Choices](#cost-implications-of-deployment-choices)  
   - [Feedback Loop Importance](#-feedback-loop-importance)  

2. [Deploy a Model as a Web Service](#02-deploy-a-model-as-a-webservice)  
   2.1 [Prepare Your Model](#021-prepare-your-model)  
   2.2 [Create a Virtual Environment](#022-create-a-virtual-environment)  
   2.3 [Build Your Prediction Script](#023-build-your-prediction-script-predictpy)  
   2.4 [Wrap Prediction in a Flask API](#024-wrap-prediction-in-a-flask-api)  
   2.5 [Use Gunicorn for Production-like Server](#025-use-gunicorn-for-production-like-server)  
   2.6 [Create a Dockerfile to Containerize the Application](#026--create-a-dockerfile-to-containerize-the-application)  
   2.7 [Build and Run Docker Container](#-027-build-and-run-docker-container)  
   2.8 [Test the Dockerized API](#028-test-the-dockerized-api)  

3. [03.1 Getting the models from the model registry (MLflow)](#031-getting-the-models-from-the-model-registry-mlflow)

--

## Key Insights

<img src="./imgs/deployment-overview.png" width="30%">

Deployment strategies must be tailored to specific use cases for optimal performance. While batch processing works well for campaigns focused on historical data, web services are indispensable in low-latency scenarios, and streaming suits dynamic, real-time environments. The key lies in balancing effectiveness with resource management and user expectations.

- **📈 Batch Mode Deployment:** This mode is efficient for situations where immediate action is unneeded. By periodically processing historical data (e.g., user churn in marketing), organizations can devise strategies without real-time pressures. However, the challenge lies in the delayed insights and subsequent actions that may become obsolete over time, and it may require continuous monitoring of data relevance.

- **🌐 Web Service Deployment:** Web services are essential for applications requiring instantaneous responses. They allow for direct communication between client applications and deployed models, serving user requests in real-time. This setup can quickly become a bottleneck if the model is not optimized for performance because the service must handle concurrent requests without significant latency, impacting user experience.

- **🔄 Streaming Architecture:** This architecture facilitates a more flexible model that can respond to real-time events. In applications like ride-sharing or content moderation, various services can consume the same stream of data, leading to faster and more dynamic adaptations. However, managing complexity and ensuring data consistency can be a significant challenge as more consumers are added to the service.

    -**💡 Scalability of Streaming Models:** Streaming allows adding new services as consumers seamlessly without affecting existing operations. This flexibility can evolve a deployment from a simple model to a robust system capable of scaling with user demands, ideal for organizations aiming to innovate rapidly in their service offerings.

### Cost Implications of Deployment Choices
Different deployment methods come with varying cost structures. Batch jobs tend to be lower in operational costs due to less frequent execution, while maintaining web services can become expensive due to constant uptime requirements. Organizations need to analyze their budget in relation to their deployment strategy.

### 🔄 Feedback Loop Importance
Each deployment strategy can benefit from feedback systems. In streaming architectures, real-time feedback can be collected and used for immediate adjustments, enhancing the model over time. In contrast, batch processing might rely more heavily on back-testing results, which can lead to longer iteration cycles in terms of improvements.


## 02. Deploy a model as a webservice

📺 [Link to the video tutorial](https://www.youtube.com/watch?v=D7wfMAdgdF8)

### 02.1 Prepare Your Model
- Start with [a machine learning model saved as a pickle](./web_service/lin_reg.bin) (.bin) file.

- Ensure you have the exact version of the model dependencies (e.g., scikit-learn) used when creating the model because unpickling with a different version can cause errors. You can run in the terminal `pip freeze | grep scikit-learn` or `python -c "import sklearn; print(sklearn.__version__)"`

### 02.2 Create a Virtual Environment
Use pipenv (or another virtual environment tool) to isolate your project dependencies:
`pipenv install scikit-learn==1.5.1 flask  --python 3.12.2`

Activate the environment:
`pipenv shell`

This ensures consistency in dependencies and runtime, matching your development environment.

### 02.3 Build Your Prediction Script ([`predict.py`](./web_service/predict.py))
Create a Python script that:
- Loads the pickle model file in read mode.
- Defines a prepare_features function for feature engineering (e.g., combining pickup and dropoff IDs into a composite feature).
- Defines a predict function which transforms input features and calls the model’s .predict() method.
- Optionally, create a test.py file that imports predict.py and runs prediction tests locally.

Summary of main parts:

```py
import pickle 
from flask import Flask, request, jsonify

with open("model.bin", "rb") as f_in:
    dv, model = pickle.load(f_in)

def prepare_features(ride):
    pu_do = f"{ride['pickup_location_id']}_{ride['dropoff_location_id']}"
    features = { "pu_do": pu_do, "trip_distance": ride["trip_distance"], }
    return features 

def predict(features):
    X = dv.transform([features])
    prediction = model.predict(X)[0]
    return prediction
```

### 02.4 Wrap Prediction in a Flask API
- Initialize a Flask app instance.
- Create an endpoint (e.g., /predict) that accepts POST requests with JSON payload containing ride data.

The endpoint:
- Extracts ride features from the request.
- Prepares features and predicts the trip duration.
- Returns a JSON response with the prediction.

You can test if the app works after you started the server with `pipenv shell`, run `python predict.py` to start the app. Then in another terminal, try the `python test.py`

### 02.5 Use Gunicorn for Production-like Server
Flask’s built-in server is for development only and shows warnings for production use.

- Install Gunicorn:
`pipenv install gunicorn`

- Run your Flask app with Gunicorn:
`gunicorn --bind 0.0.0.0:9696 predict:app`

    - Note: Here, `predict:app` means: from `predict.py`, use the app object

This command points Gunicorn to the Flask app instance in `predict.py`, enabling a production-ready WSGI server.

### 02.6  Create a Dockerfile to Containerize the Application
- Use an official lightweight Python 3.12 image as base:
`FROM python:3.12.10-slim`

- Set working directory inside the container:
`WORKDIR /app`

- Copy dependency manifest files and install dependencies via pipenv or pip:
```bash
COPY Pipfile Pipfile.lock /app/ 
RUN pip install --upgrade pip RUN pip install pipenv 
RUN pipenv install --system --deploy
```

- Copy the model and prediction script:
```bash
COPY model.bin predict.py /app/
Expose port 9696 (the port Flask app runs on):
EXPOSE 9696
```

- Define the command to run the app via Gunicorn:
`CMD ["gunicorn", "--bind", "0.0.0.0:9696", "predict:app"]`

- Full [dockerfile](./web_service/Dockerfile)

###  02.7 Build and Run Docker Container
- Build the Docker image with a tag:
`docker build -t duration-prediction-service:v1 .` 

- Run the docker container mapping port 9696:
`docker run -it --rm -p 9696:9696 duration-prediction-service:v1`

Your Flask API is now running inside the container, accessible via localhost:9696.

### 02.8 Test the Dockerized API
Use the same test script or curl to send requests to the Docker container:

```bash
curl -X POST http://localhost:9696/predict \
  -H "Content-Type: application/json" \
  -d '{"PULocationID": 10, "DOLocationID": 50, "trip_distance": 40}'
```

You should receive a JSON response with the prediction.

You can now deploy this Docker container on any platform with Docker support such as AWS Elastic Beanstalk, Kubernetes, or others for production use. 🥳

## 03.1 Getting the models from the model registry (MLflow)

[This tutorial](https://www.youtube.com/watch?v=aewOpHSCkqI) builds on a prior setup where a linear regression model was deployed as a Flask web service. Now, we enhance it by fetching models directly from the MLflow model registry using run IDs, managing model artifacts better, and removing dependencies on the MLflow tracking server.

### 03.1 Step 1: Prepare the ML Model with MLflow
- Train a Random Forest model locally or remotely.
- Use `mlflow.sklearn.log_model` to log the model.
- Log the dictionary vectorizer separately as an artifact initially.
- Store model parameters and metrics as part of the MLflow run.
- Once your experiment is logged, you will have a run ID to identify your model version uniquely.

- **Updated [project structure](./web_service_mlflow/)**

```bash
web-service-mlflow/
├── Dockerfile
├── Pipfile
├── Pipfile.lock
├── predict.py
├── mlruns/                  # stores your MLflow logs
└── random-forest.py                 # ← New: a script that logs to MLflow
```

- Start mlflow server
```bash
mlflow server \
  --backend-store-uri ./mlruns \
  --artifacts-destination ./artifacts \
  --serve-artifacts \
  --host 0.0.0.0 \
  --port 5001
```

- Train [a new model](./web_service_mlflow/random-forest.ipynb)
(make sure this model is tested here, in this order, as you could face issues with path due to local deployment)

- Run the docker container

```bash
docker run -it --rm -p 9696:9696 \
  -e MLFLOW_TRACKING_URI=http://host.docker.internal:5001 \
  -e RUN_ID=486c91b7aae84fae8d84eef0332d8573 \
  duration-prediction-service-mlflow:v1
```

- test the dockerized API
```bash
curl -X POST http://localhost:9696/predict \
  -H "Content-Type: application/json" \
  -d '{"PULocationID": 10, "DOLocationID": 50, "trip_distance": 40}'
```