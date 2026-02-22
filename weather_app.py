import datetime as dt
import requests

import json
from flask import Flask, jsonify, request

API_TOKEN = "API_TOKEN"
WEATHER_KEY = "WEATHER_KEY"

app = Flask(__name__)

def get_weather_data(location, date):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date}?unitGroup=metric&key={WEATHER_KEY}&contentType=json"
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        return response.json()
    return None

class InvalidUsage(Exception):
    status_code = 400
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/")
def home_page():
    return "<h1>KMA HW1: Weather.</h1>"

@app.route("/content/api/v1/integration/generate", methods=["POST"])
def weather_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()
    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)
    token = json_data.get("token")
    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)
    location = json_data.get("location")
    date = json_data.get("date")
    requester_name = json_data.get("requester_name")
    weather_json = get_weather_data(location, date)
    if not weather_json:
        raise InvalidUsage("External API error", status_code=500)
    result = {
        "requester_name": requester_name,
        "timestamp": start_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "location": location,
        "date": date,
        "weather": {
            "temp_c": weather_json['days'][0].get("temp"),
            "wind_kph": weather_json['days'][0].get("windspeed"),
            "pressure_mb": weather_json['days'][0].get("pressure"),
            "humidity": weather_json['days'][0].get("humidity")
        }
    }
    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
