from os import environ
from dotenv import load_dotenv
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin

load_dotenv()
AUTH_PASSWORD = environ.get("AUTH_PASSWORD")

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/", methods=["GET"])
@cross_origin()
def get_picam():
    if request.args.get("auth") == AUTH_PASSWORD:
        return "hello world"
    else:
        return Response("Unauthorised", status=401)

app.run(host='0.0.0.0', threaded=True)
