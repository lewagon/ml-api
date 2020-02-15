# Taxi Fare Prediction Model as an API

<img src="https://storage.googleapis.com/kaggle-competitions/kaggle/10170/logos/header.png">

## Summary
The goal of this tutorial is to show you how to make your [Kaggle Taxi Fare Prediction Model](https://www.kaggle.com/c/new-york-city-taxi-fare-prediction) available as a public endpoint. At the end of this tutorial, you should have a running web application endpoint that lets you estimate a NYC taxi fare based on pickup and drop-off locations.

See a live example [here](https://taxi-fare-api-wagon.appspot.com/predict_fare?passenger_count=3&dropoff_location=40,-74.3&pickup_location=40,-74).

### What you should already have
- A Google Cloud Platform (GCP) account
- A GCP project
- Service account for your AI platform project. (If not, please refer to this [page](https://cloud.google.com/docs/authentication/production#obtaining_and_providing_service_account_credentials_manually))
- A model trained on AI platform for the Taxi Fare Prediction model.
- Some code that lets you make predictions based on this trained model

## Setup a Flask Application

You are going to create a [Flask](https://flask.palletsprojects.com/en/1.1.x/) application.

First of all, create an isolated Python environment in a new directory for your project and activate it

```
mkdir taxi_fare_app && cd taxi_fare_app
python3 -m venv env
source env/bin/activate
```

Create a `requirements.txt` file to define your dependencies

```
touch requirements.txt
```
In `requirements.txt` add the following dependencies

```
flask==1.1.1
google-api-python-client==1.7.11
pytz==2019.3
```

Create a `main.py` which will be the app entry-point

```
touch main.py
```

```python
# main.py

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
  return 'OK'

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
```

Now, run you app locally with `python main.py` and go to http://127.0.0.1:8080/ to make sure it is working.


## Get Taxi Fare Model Predictions

Now, add a new route to the Flask application to call your Taxi Fare Model.
In `main.py` add the following code:

```python
from flask import request
from datetime import datetime
import pytz
import googleapiclient.discovery

PROJECT_ID="wagon-bootcamp-256007"
MODEL = "taxi_fare_prediction_model"
VERSION = "pipeline_v9"
NYC_DEFAULT_LOC = "40.7808,-73.9772"

def predict_json(project, model, instances, version=None):
  service = googleapiclient.discovery.build('ml', 'v1')
  name = 'projects/{}/models/{}'.format(project, model)
  if version is not None:
    name += '/versions/{}'.format(version)
  response = service.projects().predict(name=name, body={'instances': instances}).execute()
  if 'error' in response:
    raise RuntimeError(response['error'])
  return response["predictions"]

@app.route('/predict_fare')
def predict_fare():
  pickup_location = request.args.get("pickup_location", NYC_DEFAULT_LOC).split(",")
  dropoff_location = request.args.get("dropoff_location", NYC_DEFAULT_LOC).split(",")
  passenger_count = request.args.get("passenger_count", 1)
  pickup_datetime = datetime.utcnow().replace(tzinfo=pytz.timezone('America/New_York'))

  params = {
    "pickup_latitude": float(pickup_location[0]),
    "pickup_longitude": float(pickup_location[1]),
    "dropoff_latitude": float(dropoff_location[0]),
    "dropoff_longitude": float(dropoff_location[1]),
    "passenger_count": float(passenger_count),
    "pickup_datetime": str(pickup_datetime),
  }
  results = predict_json(project=PROJECT_ID,
                         model=MODEL,
                         instances=[params],
                         version=VERSION)
  return {
    'fare': results[0],
    'params': params
  }
```

- Fill `PROJECT_ID` with your own GCP project id
- FIll `MODEL` and `VERSION` with the model name and version you want to use.

**Warning**: Depending on the model you have, `instances` might have a different format or different keys.

Now test that you can obtain taxi fare predictions by changing the inpput parameters.

Example

http://127.0.0.1:8080/predict_fare?passenger_count=3&dropoff_location=40,-74.3&pickup_location=40,-74 

## Deploy your app to Google Cloud

Now you are going to deploy the app to the Cloud using [Google App Engine](https://cloud.google.com/appengine).

**1. Download and install [GCloud SDK](https://cloud.google.com/sdk/docs/).**

**Note**: If you already have the Cloud SDK installed, update it by running the following command `gcloud components update`

**2. Initialize a new App Engine app with your project and choose its region**

```
gcloud app create --project=[YOUR_PROJECT_ID] --region=europe-west
```

`[YOUR_PROJECT_ID]` is the id of the GCP project you created to train your model on AI Platform.

**3. Install the gcloud component that includes the App Engine extension for Python 3.7**

```
gcloud components install app-engine-python
```

**4. Create a new file `app.yaml` and add the following configuration code**

```yaml
runtime: python37
env_variables:
  GOOGLE_APPLICATION_CREDENTIALS: credentials.json
```

`GOOGLE_APPLICATION_CREDENTIALS` env variable is used to tell the app to authenticate to Google AI Platform. To do this, add a new file `credentials.json` with the content of your service account credentials. Also, make sure you create a `.gitignore` file with this content to make sure you keep these credentials private.

```
credentials.json
```

_Note: To learn more about `app.yaml` please refer to this [doc](https://cloud.google.com/appengine/docs/standard/python3/config/appref)._


**5. Deploy the app**

```
gcloud app deploy
```

**6. Launch your browser to view the app at [https://YOUR_PROJECT_ID.appspot.com](https://YOUR_PROJECT_ID.r.appspot.com)**

You can use `gcloud app browse` to directly view the app in your browser.

Then play with it by requesting taxi fare estimates

[https://YOUR_PROJECT_ID.appspot.com/predict_fare?passenger_count=3&dropoff_location=40,-74.3&pickup_location=40,-74]()

**7. Go further**

If you want to go further, you can also build an html page with a form to ask for pickup, dropoff locations, passengers count and pickup datetime.
