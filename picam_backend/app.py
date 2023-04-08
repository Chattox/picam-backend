import io
from threading import Condition
from flask import Flask, request
from flask_cors import CORS, cross_origin

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()



app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/stream", methods=["GET"])
@cross_origin()
def get_stream():
    return "hello world"

app.run(host='0.0.0.0', threaded=True)