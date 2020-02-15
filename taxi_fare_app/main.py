from flask import Flask
from flask import request
from datetime import datetime
import googleapiclient.discovery
import pytz

app = Flask(__name__)

PROJECT_ID="<your_project_id>"
MODEL = "<your_model_name>"
VERSION = "<your_model_version>"

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

@app.route('/')
def index():
  return 'OK'

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)