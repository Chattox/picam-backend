import io
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import libcamera

from flask import Flask, Response
from flask_cors import CORS, cross_origin

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1280, 720)})
video_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
picam2.configure(video_config)
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

def stream_img():
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        

try:
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    @app.route("/stream", methods=["GET"])
    @cross_origin()
    def get_stream():
        return Response(stream_img(), mimetype='multipart/x-mixed-replace; boundary=frame')

    app.run(host='0.0.0.0', threaded=True)

finally:
    picam2.stop_recording()
