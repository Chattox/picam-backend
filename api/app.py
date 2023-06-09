from os import environ
from dotenv import load_dotenv
from flask import Flask, Response, request, json
from flask_cors import CORS, cross_origin
from picam.Picam import Picam
from temp_sensor.Temp import TempSensor

load_dotenv()
AUTH_PASSWORD = environ.get("AUTH_PASSWORD")

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

camera = Picam()
temp = TempSensor()
temp.start_temp_tracking()

@app.route("/stream", methods=["GET"])
@cross_origin()
def get_picam():
    if request.args.get("auth") == AUTH_PASSWORD:
        return Response(camera.livestream(), mimetype='multipart/x-mixed-replace; boundary=frame', status=200)
    else:
        return Response("Unauthorised", status=401)

@app.route("/temperature", methods=["GET"])
@cross_origin()
def get_temp():
    if request.args.get("auth") == AUTH_PASSWORD:
        temperature = temp.fetch_temp()
        return Response(json.dumps(temperature), mimetype='application/json', status=200)